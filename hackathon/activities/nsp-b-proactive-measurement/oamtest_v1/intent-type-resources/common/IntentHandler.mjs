/********************************************************************************
 * COMMON INTENT HANDLER IMPLEMENTATION
 * 
 * (c) 2024 by Nokia
 ********************************************************************************/

/* global classResolver, Java */
/* global mds, logger, restClient, resourceProvider, utilityService, topologyFactory */
/* eslint no-undef: "error" */

import { IntentLogic } from "common/IntentLogic.mjs";
import { CalloutHandler } from "common/CalloutHandler.mjs";

let ValidateResult = classResolver.resolveClass("com.nokia.fnms.controller.ibn.intenttype.spi.ValidateResult");
let SynchronizeResult = classResolver.resolveClass("com.nokia.fnms.controller.ibn.intenttype.spi.SynchronizeResult");
let AuditReport = classResolver.resolveClass("com.nokia.fnms.controller.ibn.intenttype.spi.AuditReport");
let MisAlignedObject = classResolver.resolveClass("com.nokia.fnms.controller.ibn.intenttype.spi.MisAlignedObject");
let MisAlignedAttribute = classResolver.resolveClass("com.nokia.fnms.controller.ibn.intenttype.spi.MisAlignedAttribute");

let ArrayList = classResolver.resolveClass("java.util.ArrayList");

export class IntentHandler extends CalloutHandler
{
  #logic;
  #deviceCache;
  #dcLastUpdated;

  /**
    * Create IntentHandler
    * 
    * @param {IntentLogic} intentLogic
    * 
    **/

  constructor(intentLogic)
  {
    super();    
    this.#logic = intentLogic;
    this.#deviceCache = {};
    this.#dcLastUpdated = -1;
  }

  /**
    * Retrieve device configuration/state using device model (RESTCONF GET / MDC)
    * 
    * @param {} neId 
    * @param {} path 
    * @returns success {boolean} and respone {dict} or errmsg {string}
    * 
    **/

  #restconfGetDevice(neId, path) {
    const startTS = Date.now();
    logger.debug("IntentHandler::#restconfGetDevice({}, {})", neId, path);

    var result = {};
    const managerInfo = mds.getAllManagersWithDevice(neId).get(0);
    if (managerInfo.getConnectivityState().toString() === 'CONNECTED') {
      const url = "/restconf/data/network-device-mgr:network-devices/network-device="+neId+"/root/"+path;

      restClient.setIp(managerInfo.getIp());
      restClient.setPort(managerInfo.getPort());
      restClient.setProtocol(managerInfo.getProtocol().toString());

      restClient.get(url, "application/json", (exception, httpStatus, response) => {
        const duration = Date.now()-startTS;
        logger.info("GET {} finished within {} ms", url, duration|0);

        if (exception) {
          logger.error("Exception {} occured.", exception);
          result = { success: false, errmsg: "Couldn't connect to mediator. Exception "+exception+" occured." };
        }
        else if (httpStatus >= 400) {
          // Either client error (4xx) or server error (5xx)

          // Note:
          // 404 (resource not found) is considered a normal case, while it might happen during
          // audits when the resource was not yet created. To avoid confusing developers getting
          // in panic when reading the logs, status-code 404 using log-level info instead of warn

          if (httpStatus === 404) {
            logger.info("NSP response: {} {}", httpStatus, response);  
          }
          else
            logger.warn("NSP response: {} {}", httpStatus, response);  

          // Error details returned in accordance to RFC8020 ch7.1
          //   {"ietf-restconf:errors":{"error":[{ ___error details__ }]}}
          //
          // Error fields:
          //   error-type       enumeration
          //   error-tag        string
          //   error-app-tag?   string
          //   error-path?      instance-identifier
          //   error-message?   string
          //   error-info?      anydata

          var errmsg = "HTTP ERROR "+httpStatus;          
          switch (httpStatus) {
            case 400:
              // invalid request (should not happen)
              errmsg = "Bad Request"; break;
            case 401:
              // access-control related (should not happen)
              errmsg = "Unauthorized (access-denied)";
              break;
            case 403:
              // access-control related (should not happen)
              errmsg = "Forbidden";
              break;
            case 404:
              // resource does not exist
              errmsg = "Not Found";
              break;
            case 405:
              // operation resource (should not happen)
              errmsg = "Method Not Allowed";
              break;
          }

          result = { success: false, errmsg: errmsg };
        }
        else {
          // Should be 200 OK
          if (response.length > 2048)
            logger.info("NSP response: {}, received {} bytes", httpStatus, response.length);
          else 
            logger.info("NSP response: {} {}", httpStatus, response);
          result = { success: true, response: JSON.parse(response) };
        }
      });
    } else {
      logger.error("Mediator for {} is disconneted.", neId);
      result = { success: false, errmsg: "Mediator for "+neId+" is disconnected." };
    }

    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#restconfGetDevice() finished within {} ms", duration|0);

    return result;
  }

  /**
    * Edit device configuration using device model (RESTCONF PATCH / MDC)
    * 
    * @param {} neId target device
    * @param {} body SON string (rfc8072 YANG PATCH compliant)
    * @returns success {boolean}, response {object}, errmsg {string}
    * 
    **/

  #restconfPatchDevice(neId, body) {
    const startTS = Date.now();
    logger.debug("IntentHandler::#restconfPatchDevice({})", neId);

    var result = {};
    const managerInfo = mds.getAllManagersWithDevice(neId).get(0);
    if (managerInfo.getConnectivityState().toString() === 'CONNECTED') {
      const url = "/restconf/data/network-device-mgr:network-devices/network-device="+neId+"/root/";

      restClient.setIp(managerInfo.getIp());
      restClient.setPort(managerInfo.getPort());
      restClient.setProtocol(managerInfo.getProtocol().toString());

      restClient.patch(url, "application/yang-patch+json", body, "application/yang-data+json", (exception, httpStatus, response) => {
        const duration = Date.now()-startTS;
        logger.info("PATCH {} {} finished within {} ms", url, body, duration|0);

        if (exception) {
          logger.error("Exception {} occured.", exception);
          result = { success: false, errmsg: "Couldn't connect to mediator. Exception "+exception+" occured." };
        }
        else if (httpStatus >= 400) {
          // Either client error (4xx) or server error (5xx)
          logger.warn("NSP response: {} {}", httpStatus, response);

          let errmsg="";
          if ((/<html/i).test(response)) {
            // Extract error details from HTML response:
            const errMatch = response.match(/<body[^>]*>(.*)<\/body>/i);
            if (errMatch)
              errmsg = errMatch[1]; // extracted errmsg from html body
            else
              errmsg = "HTTP ERROR "+httpStatus;
          } else {
            // Extract error details from JSON response:
            //
            // Error details returned in accordance to RFC8072 ch2.3 (2 options: global errors OR edit errors )
            //   {"ietf-yang-patch:yang-patch-status":{"ietf-restconf:errors":{"error":[{ error details }]}}}
            //   {"ietf-yang-patch:yang-patch-status":{"edit-status":{"edit":[{"ietf-restconf:errors":{"error":[{ error details }]}}]}}}
            //
            // Error fields:
            //   error-type       enumeration
            //   error-tag        string
            //   error-app-tag?   string
            //   error-path?      instance-identifier
            //   error-message?   string
            //   error-info?      anydata          

            const errorObject = JSON.parse(response);
            if ('ietf-yang-patch:yang-patch-status' in errorObject) {
              const yangPatchStatus = errorObject['ietf-yang-patch:yang-patch-status'];

              // Check for RFC8072 YANG-PATCH ERRORS: global-errors
              if ('ietf-restconf:errors' in yangPatchStatus) {
                const errList = yangPatchStatus['ietf-restconf:errors'].error;
                errmsg = errList.map(error => error["error-message"]).join(', ');
              }

              // Check for RFC8072 YANG-PATCH ERRORS: edit-errors
              if ('edit-status' in yangPatchStatus) {
                yangPatchStatus['edit-status'].edit.forEach( edit => {
                  if (edit['edit-id'])
                    errmsg += "[object: "+edit['edit-id']+"] ";
                  const errList = edit['ietf-restconf:errors'].error;
                  errmsg += errList.map(error => {
                    if (error['error-path'])
                      return "[path: " + error['error-path'] + "] " + error['error-message'];
                    else
                      return error['error-message'];
                  }).join(', ')+" ";
                });
              }
            }
          }
          result = { success: false, errmsg: errmsg.trim() };
        } else {
          // 2xx - Success
          logger.info("NSP response: {} {}", httpStatus, response);
          result = { success: true, response: JSON.parse(response) };
        }
      });
    } else {
      logger.error("Mediator for {} is disconneted.", neId);
      result = { success: false, errmsg: "Mediator for "+neId+" is disconnected." };
    }

    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#restconfPatchDevice() finished within {} ms", duration|0);

    return result;
  }

  /**
    * Executes framework action, implemented by the mediator
    * 
    * @param {} action mediator framework action to be called
    * @param {} input dictionary of input variables (action specific)
    * @returns success {boolean}, respone {object}, errmsg {string}
    * 
    **/
  
  #fwkAction(action, input)
  {
    const startTS = Date.now();
    logger.debug("IntentHandler::#fwkAction({})", action);
    
    var result = {};
    const managerInfo = mds.getManagerByName('NSP');
    if (managerInfo.getConnectivityState().toString() === 'CONNECTED') {
      restClient.setIp(managerInfo.getIp());
      restClient.setPort(managerInfo.getPort());
      restClient.setProtocol(managerInfo.getProtocol().toString());

      restClient.post(action, "application/json", JSON.stringify(input), "application/json", (exception, httpStatus, response) => {
        const duration = Date.now()-startTS;
        logger.info("POST {} {} finished within {} ms", action, input, duration|0);

        if (exception) {
          logger.error("Exception {} occured.", exception);
          result = { success: false, errmsg: "Couldn't connect to mediator. Exception "+exception+" occured." };
        }
        else if (httpStatus >= 400) {
          logger.warn("NSP response: {} {}", httpStatus, response);
          result = { success: false, response: JSON.parse(response), errmsg: "HTTP ERROR "+httpStatus };

        }
        else {
          logger.debug("NSP response: {} {}", httpStatus, response);
          result = { success: true, response: JSON.parse(response) };
        }
      });
    } else {
      logger.error("NSP mediator is disconneted.");
      result = { success: false, errmsg: "NSP mediator is disconnected." };
    }

    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#fwkAction() finished within {} ms", duration|0);

    return result;
  }

  #updateDeviceCache() {
    const startTS = Date.now();

    if (startTS - this.#dcLastUpdated < 300000)
      // Keep cache! Content was updated within the last 5min
      return;

    this.#dcLastUpdated = startTS;
    logger.debug("IntentHandler::#updateDeviceCache()");
    
    var managerInfo = mds.getManagerByName('NSP');
    if (managerInfo.getConnectivityState().toString() === 'CONNECTED') {
      restClient.setIp(managerInfo.getIp());
      restClient.setPort(managerInfo.getPort());
      restClient.setProtocol(managerInfo.getProtocol().toString());
    
      var url = "https://restconf-gateway/restconf/operations/nsp-inventory:find";
      var options = {
        "xpath-filter": "/nsp-equipment:network/network-element",
        "depth": 3,
        "fields": "ne-id;ne-name",
        "offset": 0,
        'include-meta': false
      };

      let total=1;
      let offset=0;
      let newCache = {};

      while (offset<total) {
        options.offset = offset;
        restClient.post(url, "application/json", JSON.stringify({"input": options}), "application/json", (exception, httpStatus, response) => {
          if (exception) {
            logger.error("Exception {} occured.", exception);
            this.#dcLastUpdated = -1;
            total = offset;
          }
          else if (httpStatus >= 400) {
            // Either client error (4xx) or server error (5xx)
            logger.warn("NSP response: {} {}", httpStatus, response);
            this.#dcLastUpdated = -1;
            total = offset;
          }
          else {
            const output = JSON.parse(response)["nsp-inventory:output"];
            total = output["total-count"];
            offset = output["end-index"]+1;
            output.data.forEach(entry => newCache[entry['ne-id']] = entry['ne-name']);
          }
        });
      }

      this.#deviceCache = newCache;
      this.#dcLastUpdated = Date.now();
      logger.info("device cache updated: {} entries", total);
    }

    const duration = Date.now()-startTS;
    logger.debug("CalloutHandler::#updateDeviceCache() finished within {} ms", duration|0);    
  }
  
  /**
    * Get list-keys from YANG model for MDC-managed nodes
    *
    * @param {} neId device
    * @param {} listPath  path of list to get the keys
    * @returns listKeys[]
    *
    **/
  
  #getListKeys(neId, listPath) {
    const startTS = Date.now();
    logger.debug("IntentHandler::#getListKeys({}, {})", neId, listPath);

    var result = {};
    const managerInfo = mds.getManagerByName('NSP');
    if (managerInfo.getConnectivityState().toString() === 'CONNECTED') {
      const url = "https://restconf-gateway/restconf/meta/api/v1/model/schema/"+neId+"/"+listPath.replace(/=[^=/]+\//g, "/");
      
      restClient.setIp(managerInfo.getIp());
      restClient.setPort(managerInfo.getPort());
      restClient.setProtocol(managerInfo.getProtocol().toString());

      restClient.get(url, "application/json", (exception, httpStatus, response) => {
        if (exception)
          result = { success: false, errmsg: "Couldn't connect to mediator. Exception "+exception+" occured." };
        else if (httpStatus === 200)
          result = { success: true, response: JSON.parse(response) };
        else if (httpStatus === 201)
          result = { success: false, errmsg: "Returned httpStatus(201): No response" };
        else
          result = { success: false, errmsg: response };
      });
    } else
      result = { success: false, errmsg: "NSP mediator is disconnected." };
    
    var listKeys = [];
    if (result["success"]) {
      const attr = result["response"]["attributes"];
      for (var i = 0; i<attr.length; i++) {
        if(attr[i]["isKey"] !== undefined) {
          listKeys.push(attr[i]["name"]);
        }
      }
    } else
      logger.error("#getListKeys() failed with {}", result["errmsg"]);
    
    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#getListKeys({}, {}) finished within {} ms", neId, listPath, duration|0);

    return listKeys;
  }

  /**
    * JSONPath 0.8.4 - XPath for JSON
    * available from https://code.google.com/archive/p/jsonpath/
    *
    * Copyright (c) 2007 Stefan Goessner (goessner.net)
    * Licensed under the MIT (MIT-LICENSE.txt) licence.
    * 
    * @param {} obj
    * @param {} expr
    * @param {} arg
    * @returns result
    * 
    * @throws SyntaxError
    *
    **/

  #jsonPath(obj, expr, arg) {
    var P = {
      resultType: arg && arg.resultType || "VALUE",
      result: [],
      normalize: function(expr) {
         var subx = [];
         return expr.replace(/[['](\??\(.*?\))[\]']|\['(.*?)'\]/g, function($0,$1,$2){return "[#"+(subx.push($1||$2)-1)+"]";})
                    .replace(/'?\.'?|\['?/g, ";")
                    .replace(/;;;|;;/g, ";..;")
                    .replace(/;$|'?\]|'$/g, "")
                    .replace(/#([0-9]+)/g, function($0,$1){return subx[$1];});
      },
      asPath: function(path) {
         var x = path.split(";"), p = "$";
         for (var i=1,n=x.length; i<n; i++)
            p += /^[0-9*]+$/.test(x[i]) ? ("["+x[i]+"]") : ("['"+x[i]+"']");
         return p;
      },
      store: function(p, v) {
         if (p) P.result[P.result.length] = P.resultType == "PATH" ? P.asPath(p) : v;
         return !!p;
      },
      trace: function(expr, val, path) {
         if (expr !== "") {
            var x = expr.split(";"), loc = x.shift();
            x = x.join(";");
            if (val && Object.prototype.hasOwnProperty.call(val, loc))
               P.trace(x, val[loc], path + ";" + loc);
            else if (loc === "*")
               P.walk(loc, x, val, path, function(m,l,x,v,p) { P.trace(m+";"+x,v,p); });
            else if (loc === "..") {
               P.trace(x, val, path);
               P.walk(loc, x, val, path, function(m,l,x,v,p) { typeof v[m] === "object" && P.trace("..;"+x,v[m],p+";"+m); });
            }
            else if (/^\(.*?\)$/.test(loc)) // [(expr)]
               P.trace(P.eval(loc, val, path.substr(path.lastIndexOf(";")+1))+";"+x, val, path);
            else if (/^\?\(.*?\)$/.test(loc)) // [?(expr)]
               P.walk(loc, x, val, path, function(m,l,x,v,p) { if (P.eval(l.replace(/^\?\((.*?)\)$/,"$1"), v instanceof Array ? v[m] : v, m)) P.trace(m+";"+x,v,p); });
            else if (/^(-?[0-9]*):(-?[0-9]*):?([0-9]*)$/.test(loc)) // [start:end:step]  phyton slice syntax
               P.slice(loc, x, val, path);
            else if (/,/.test(loc)) { // [name1,name2,...]
               for (var s=loc.split(/'?,'?/),i=0,n=s.length; i<n; i++)
                  P.trace(s[i]+";"+x, val, path);
            }
         }
         else
            P.store(path, val);
      },
      walk: function(loc, expr, val, path, f) {
         if (val instanceof Array) {
            for (var i=0,n=val.length; i<n; i++)
               if (i in val)
                  f(i,loc,expr,val,path);
         }
         else if (typeof val === "object") {
            for (var m in val)
              if (Object.prototype.hasOwnProperty.call(val, m))
                  f(m,loc,expr,val,path);
         }
      },
      slice: function(loc, expr, val, path) {
         if (val instanceof Array) {
            var len=val.length, start=0, end=len, step=1;
            loc.replace(/^(-?[0-9]*):(-?[0-9]*):?(-?[0-9]*)$/g, function($0,$1,$2,$3){start=parseInt($1||start);end=parseInt($2||end);step=parseInt($3||step);});
            start = (start < 0) ? Math.max(0,start+len) : Math.min(len,start);
            end   = (end < 0)   ? Math.max(0,end+len)   : Math.min(len,end);
            for (var i=start; i<end; i+=step)
               P.trace(i+";"+expr, val, path);
         }
      },
      eval: function(x, _v, _vname) {
         try { return $ && _v && eval(x.replace(/@/g, "_v")); }
         catch(e) { throw new SyntaxError("jsonPath: " + e.message + ": " + x.replace(/@/g, "_v").replace(/\^/g, "_a")); }
      }
    };

    var $ = obj;
    if (expr && obj && (P.resultType == "VALUE" || P.resultType == "PATH")) {
       P.trace(P.normalize(expr).replace(/^\$;?/,""), obj, "$");
       return P.result.length ? P.result : false;
    }
  }

  /**
    * Wrapper for /resolve-synchronize implemented in mediator (since nsp23.11).
    * Merges desired config with actual config to keep approved misalignments untouched.
    *
    * @param {string} target     Intent target
    * @param {string} neId       Device identifier
    * @param {string} rootXPath  Root XPATH of configuration
    * @param {Object} config     Desired configuration
    * 
    * @throws {Error} /resolve-synchronize failed
    * 
    **/

  #resolveSynchronize(target, neId, rootXPath, config) {
    const startTS = Date.now();
    logger.debug("IntentHandler::#resolveSynchronize({}, {}, {})", target, neId, rootXPath);

    const unresolvedConfig = {
        "intent-type": this.#logic.INTENT_TYPE,
        "target": target,
        "device-name": neId,
        "root-xpath": rootXPath,
        "intent-configuration": config
    };
    const resolveResponse = this.#fwkAction("/resolve-synchronize", unresolvedConfig);
    if (!resolveResponse.success)
      throw new Error("Resolve Synchronize failed with {}", resolveResponse.errmsg);      

    // enable for detailed debugging:
    // logger.info("desired config:  {}", JSON.stringify(config));
    // logger.info("resolved config: {}", JSON.stringify(resolveResponse.response));

    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#resolveSynchronize() finished within {} ms", duration|0);

    return resolveResponse.response;
  }

/**
  * Wrapper for /resolve-audit implemented in mediator (since nsp23.11).
  * Removes approved attributes/objects from audit-report.
  *
  * @param {string} target Intent target
  * @param {AuditReport} auditReport Audit report before applying approvals
  * 
  * @throws {Error} /resolve-audit failed
  * 
  **/

  #resolveAudit(auditReport) {
    const startTS = Date.now();
    logger.debug("IntentHandler::#resolveAudit()");
  
    // Convert audit report to JSON
    const auditReportJson = {
      "target": auditReport.getTarget(),
      "intent-type": auditReport.getIntentType()
    };

    if (auditReport.getMisAlignedAttributes()) {
        auditReportJson["misaligned-attribute"] = [];
        auditReport.getMisAlignedAttributes().forEach(misAlignedAttribute => {
            const misAlignedAttributeJson = {
                "name": misAlignedAttribute.getName(),
                "device-name": misAlignedAttribute.getDeviceName(),
                "expected-value": misAlignedAttribute.getExpectedValue(),
                "actual-value": misAlignedAttribute.getActualValue(),
            };
            auditReportJson["misaligned-attribute"].push(misAlignedAttributeJson);
        });
    }

    if (auditReport.getMisAlignedObjects()) {
        auditReportJson["misaligned-object"] = [];
        auditReport.getMisAlignedObjects().forEach(misAlignedObject => {
            const misAlignedObjectJson = {
                "object-id": misAlignedObject.getObjectId(),
                "device-name": misAlignedObject.getDeviceName(),
                "is-configured": misAlignedObject.isConfigured(),
                "is-undesired": misAlignedObject.isUndesired()
            };
            auditReportJson["misaligned-object"].push(misAlignedObjectJson);
        });
    }

    // Call the mediator to resolve audit report
    let resolveResponse = this.#fwkAction("/resolve-audit", auditReportJson);
    if (!resolveResponse.success)
      throw new Error("/resolve-audit failed with {}", resolveResponse.errmsg);

    const resolvedAuditReportJson = resolveResponse.response;
    logger.info("resolved audit report:\n{}", JSON.stringify(resolvedAuditReportJson, null, "  "));

    // Create a new audit report to send back
    const resolvedAuditReport = new AuditReport();
    resolvedAuditReportJson["misaligned-attribute"].forEach(entry =>
      resolvedAuditReport.addMisAlignedAttribute(new MisAlignedAttribute(entry.name, entry["expected-value"], entry["actual-value"], entry["device-name"]))
    );
    resolvedAuditReportJson["misaligned-object"].forEach(entry =>
      resolvedAuditReport.addMisAlignedObject(new MisAlignedObject(entry["object-id"], entry["is-configured"], entry["device-name"], entry["is-undesired"]))
    );

    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#resolveAudit() finished within {} ms", duration|0);

    return resolvedAuditReport;
  }

/**
  * Audit helper to compare intented vs actual config
  *
  * @param {} neId required for fetching model info
  * @param {} basePath target root path of the object under audit
  * @param {} aCfg actual config (object)
  * @param {} iCfg intended config (object)
  * @param {} mode operation: create, replace, merge, delete
  * @param {} ignore list of children subtree to ignore
  * @param {} auditReport used to report differences
  * @param {} obj object reference used for report
  * @param {} path used to build up relative path (recursive)
  *
  **/
  
  #compareConfig(neId, basePath, aCfg, iCfg, mode, ignore, auditReport, obj, path) {
    const startTS = Date.now();
    logger.debug("IntentHandler::#compareConfig(neId={}, basePath={}, path={})", neId, basePath, path);

    // enable for detailed debugging:
    // logger.info("iCfg: "+JSON.stringify(iCfg));
    // logger.info("aCfg: "+JSON.stringify(aCfg));
    
    for (const key in iCfg) {
      if (key in aCfg) {
        if (typeof iCfg[key] !== typeof aCfg[key]) {
          // mismatch: type is different
          auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+basePath+'/'+path+key, 'type '+typeof iCfg[key], 'type '+typeof aCfg[key], obj));
        } else if (!(iCfg[key] instanceof Object)) {
          if (iCfg[key] !== aCfg[key]) {
            // mismatch: value is different
            auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+basePath+'/'+path+key, iCfg[key].toString(), aCfg[key].toString(), obj));
          } else {
            // aligned: type/value are same
          }
        } else if (Array.isArray(iCfg[key])) {
          if ((iCfg[key].length > 0) && (iCfg[key][0] instanceof Object) || (aCfg[key].length > 0) && (aCfg[key][0] instanceof Object)) {
            // children is a yang list
            // group by list-key and look one level deeper
            const keys = this.#getListKeys(neId, basePath+'/'+path+key);

            const iCfgConverted = iCfg[key].reduce((rdict, entry) => {
              const value = keys.map( key => encodeURIComponent(entry[key]) ).join(",");
              rdict[value] = entry;
              return rdict; 
            }, {});

            const aCfgConverted = aCfg[key].reduce((rdict, entry) => {
              const value = keys.map( key => encodeURIComponent(entry[key]) ).join(",");
              rdict[value] = entry;
              return rdict; 
            }, {});
            
            this.#compareConfig(neId, basePath, aCfgConverted, iCfgConverted, mode, ignore, auditReport, obj, path+key+'=');
          } else {
            const iVal = JSON.stringify(iCfg[key]);
            const aVal = JSON.stringify(aCfg[key]);
            if (iVal !== aVal) {
              auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+basePath+'/'+path+key, iVal, aVal, obj));
            }
          }
        } else {
          // children is a yang container
          // look one level deeper
          this.#compareConfig(neId, basePath, aCfg[key], iCfg[key], mode, ignore, auditReport, obj, path+key+'/');
        }        
      } else {
        if (iCfg[key] instanceof Object) {
          // mismatch: list/container is unconfigured
              
          const iVal = JSON.stringify(iCfg[key]);
          if ((iVal === '{}') || (iVal === '[]') || (iVal === '[null]')) 
            auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+basePath+'/'+path+key, iVal, null, obj));
          else
            // missing object: is-configured=true, is-undesired=default(false)
            auditReport.addMisAlignedObject(new MisAlignedObject('/'+basePath+'/'+path+key, true, neId));
        } else {
          // mismatch: leaf is unconfigured
          auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+basePath+'/'+path+key, iCfg[key].toString(), null, obj));
        }
      }
    }

    // undesired nodal attributes (only in mode create/replace)
    if (mode !== 'merge') {
      for (const key in aCfg) {
        if (!(key in iCfg)) {
          // Possibility to ignore undesired children that match the list provided. Restrictions:
          //  (1) Can only ignore what is not part of the object created
          //  (2) Object created must contain the parent of the ignored
          //  (3) The ignore option is currently supported for audit only (not for deployment)
          
          let found = "";
          const aKey = path+key;
          for (const idx in ignore) {
            if (aKey.startsWith(ignore[idx])) {
              found = ignore[idx];
              break;
            }
          }
          
          if (!found) {
            if (aCfg[key] instanceof Object) {
              // mismatch: undesired list/container
              
              const aVal = JSON.stringify(aCfg[key]);
              if ((aVal === '{}') || (aVal === '[]') || (aVal === '[null]')) 
                auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+basePath+'/'+aKey, null, aVal, obj));
              else
                // undesired object: is-configured=true, is-undesired=default(true)
                auditReport.addMisAlignedObject(new MisAlignedObject('/'+basePath+'/'+aKey, true, neId, true));              
            } else {
              // mismatch: additional leaf
              auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+basePath+'/'+aKey, null, aCfg[key].toString(), obj));
            }
          }          
        }
      }
    }

    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#compareConfig(neId={}, basePath={}, path={}) finished within {} ms", neId, basePath, path,  duration|0);
  }

/**
  * Audit helper to compare intented vs actual state
  *
  * @param {} neId ne-id, required for fetching model info
  * @param {} aState actual state (object)
  * @param {} iState intended state (object)
  * @param {} auditReport used to report differences
  * @param {} obj object reference used for report
  * 
  * @throws {Error}
  * 
  **/
    
  #compareState(neId, aState, iState, auditReport, qPath) {
    const startTS = Date.now();
    logger.debug("IntentHandler::#compareState(neId={}, qPath={})", neId, qPath);

    // enable for detailed debugging:
    // logger.info("iState: "+JSON.stringify(iState));
    // logger.info("aState: "+JSON.stringify(iState));

    const siteName = neId;    
    for (const key in iState) {
      if (iState[key] instanceof Object) {
        const path = iState[key].path;
        const aValue = this.#jsonPath(aState, path);
        
        for (const check in iState[key]) {
          if (check !== 'path') {
            const iValue = iState[key][check];
            if (aValue && aValue.length > 0) {
              let match = true;
              switch (check) {
                case 'equals':
                case 'matches':
                  match = (aValue[0] === iValue);
                  break;
                case 'contains':
                case 'includes':
                  match = (aValue[0].indexOf(iValue) != -1);
                  break;
                case 'startsWith':
                  match = (aValue[0].startsWith(iValue));
                  break;
                case 'endsWith':
                  match = (aValue[0].endsWith(iValue));
                  break;
                case 'regex':
                  match = RegExp(iValue).test(aValue[0]);
                  break;
                default:
                  throw new Error("Unsupported check '"+check+"' for object("+path+"), jsonpath("+path+"), expected value("+iValue+")");
              }    
              if (!match)
                auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+qPath+'/'+key, iValue.toString(), aValue[0].toString(), siteName));
            } else {
              auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+qPath+'/'+key, iValue.toString(), null, siteName));
            }
          }
        }
      } else if (key in aState) {
        if (iState[key] !== aState[key])
          auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+qPath+'/'+key, iState[key].toString(), aState[key].toString(), siteName));
      } else {
        auditReport.addMisAlignedAttribute(new MisAlignedAttribute('/'+qPath+'/'+key, iState[key].toString(), null, siteName));
      }
    }

    const duration = Date.now()-startTS;
    logger.debug("IntentHandler::#compareState(neId={}, qPath={}) finished within {} ms", neId, qPath,  duration|0);
  }

/**
  * Validation of intent config/target that is automatically called for intent 
  * create/edit and state-change operations.
  * 
  * If the intent config is identified invalid, the create/edit operation will
  * fail. Execution happens before synchronize() to ensure intent data is valid.
  * 
  * In this particular case we are validating if the device is known to the
  * mediator and if the corresponding freemarker template (ftl) could be loaded.
  * 
  * @param {} input input provided by intent-engine
  * @returns {ValidateResult}
  * 
  * @throws ContextErrorException
  * 
  **/

  validate(input) {
    const startTS = Date.now();

    const target = input.getTarget();
    const config = JSON.parse(input.getJsonIntentConfiguration())[0][this.#logic.INTENT_ROOT];

    logger.info("IntentHandler::validate()");

    var contextualErrorJsonObj = {};
    var validateResult = new ValidateResult();

    this.#logic.getSites(target, config).forEach(neId => {
      const neInfo = mds.getAllInfoFromDevices(neId);
      
      if (neInfo === null || neInfo.size() === 0) {
        contextualErrorJsonObj["NODE "+neId] = "Node not found";
      } else {
        const neFamilyTypeRelease = neInfo.get(0).getFamilyTypeRelease();
        if (neFamilyTypeRelease === null) {
          contextualErrorJsonObj["NODE "+neId] = "Family/Type/Release unkown";
        } else {
          const neType = neFamilyTypeRelease.split(':')[0];
          const neVersion = neFamilyTypeRelease.split(':')[1];
          const templateName = this.#logic.getTemplateName(neId, neType);
          try {
            resourceProvider.getResource(templateName);
          } catch (e) {
            contextualErrorJsonObj["NODE "+neId] = "Device type unsupported! Template '"+templateName+"' not found!";
          }
        }
      }
    });

    this.#logic.validate(target, config, contextualErrorJsonObj);

    const duration = Date.now()-startTS;
    logger.info("IntentHandler::validate() finished within {} ms", duration|0);

    if (Object.keys(contextualErrorJsonObj).length !== 0)
      utilityService.throwContextErrorException(contextualErrorJsonObj);

    return validateResult;
  }

/**
  * Deployment of intents to the network, called for synchronize operations.
  * Used to apply create, update, delete and reconcile to managed devices.
  *
  * All objects created are remembered/restored as part of topology/extra-data
  * to enable update and delete operations removing network objects that are
  * no longer required (house-keeping).
  * 
  * In the deployment template (ftl) it's recommended to use operations "replace",
  * "merge", or "remove". The usage of "create" must be avoided, because it fails
  * if the network object already exists (use "replace" instead). The usage of
  * "delete" must be avoided, because it fails if the network object does not
  * exists (use "remove" instead).
  *
  * @param {SynchronizeInput} input information about the intent to be synchronized
  * @returns {SynchronizeResult} provide information about the execution/success back to the engine
  * 
  **/

  async synchronize(input) {  
    const startTS = Date.now();
    const target  = input.getTarget();
    const state   = input.getNetworkState().name();

    logger.info("IntentHandler::synchronize() in state {} ", state);

    const config  = JSON.parse(input.getJsonIntentConfiguration())[0][this.#logic.INTENT_ROOT];
     
    var topology   = input.getCurrentTopology();
    var syncResult = new SynchronizeResult();
    var syncErrors = [];

    var sitesConfigs = {};
    var sitesCleanups = {};

    try {
      // Update device-cache (as needed)
      this.#updateDeviceCache();
      
      const yangPatchTemplate = resourceProvider.getResource("common/patch.ftl");

      // Recall nodal configuration elements from previous synchronize (for cleanup/housekeeping)
      if (topology && topology.getXtraInfo()!==null && !topology.getXtraInfo().isEmpty()) {
        topology.getXtraInfo().forEach(item => {
          if (item.getKey() === 'sitesCleanups') {
            sitesCleanups = JSON.parse(item.getValue());
            sitesConfigs  = JSON.parse(item.getValue()); // deep-clone of sitesCleanups
            logger.info("sitesCleanups restored: "+item.getValue());
          }
        });
      }

      // Secure resources from Resource Admin
      // Right now, we are assuming that reservation is required in any state but delete

      if (state !== 'delete')
        this.#logic.obtainResources(target, config);

      if (state === "active") {
        const global = this.#logic.getGlobalParameters(target, config);

        // Iterate sites to populate/update sitesConfigs per target device
        this.#logic.getSiteParameters(target, config, this.#deviceCache).forEach(site => {
          const neId = site['ne-id'];
          const neInfo = mds.getAllInfoFromDevices(neId);
          const neFamilyTypeRelease = neInfo.get(0).getFamilyTypeRelease();
          const neType = neFamilyTypeRelease.split(':')[0];
          const neVersion = neFamilyTypeRelease.split(':')[1];

          // ensure we've got the user-friendly deviceName
          site['ne-name'] = this.#deviceCache[neId];

          if (!(neId in sitesConfigs))
            sitesConfigs[neId] = {};

          const siteFTL = resourceProvider.getResource(this.#logic.getTemplateName(neId, neType));
          const objects = JSON.parse(utilityService.processTemplate(siteFTL, {'target': target, 'site': site, 'global': global, 'neVersion': neVersion, 'mode': 'sync'}));
            
          for (const objectName in objects) {
            if ("config" in objects[objectName]) {
              sitesConfigs[neId][objectName] = objects[objectName].config;
                  
              // Convert 'value' object to JSON string as required as input for PATCH.ftl
              if (objects[objectName].config.value) {
                let value = this.#resolveSynchronize(target, neId, '/'+objects[objectName].config.target, objects[objectName].config.value);
                sitesConfigs[neId][objectName].value = JSON.stringify(value);
              }
            }
          }
        });
      }

      // Deploy changes to target devices and update topology objects and xtra-data
      if (state === "active" || state === "suspend" || state === "delete") {
        let topologyObjects = [];
        for (const neId in sitesConfigs) {
          const body = utilityService.processTemplate(yangPatchTemplate, {'patchId': target, 'patchItems': sitesConfigs[neId]});
          
          let result = this.#restconfPatchDevice(neId, body);
          
          if (result.success) {
            // RESTCONF YANG PATCH was successful
            //  - objects that have been added/updated are added to the new topology
            //  - objects that have been added/updated are added to siteCleanups (extraData) to enable housekeeping
            
            sitesCleanups[neId] = {};
            for (const objectName in sitesConfigs[neId]) {
              if (sitesConfigs[neId][objectName]["operation"]==="replace") {
                // For operation "replace" remember how to clean-up the object created (house-keeping).
                // For cleanup we are using operation "remove", to avoid the operation from failing,
                // if the corresponding device configuration was deleted from the network already.
                
                sitesCleanups[neId][objectName] = {'target': sitesConfigs[neId][objectName].target, 'operation': 'remove'};
                topologyObjects.push(topologyFactory.createTopologyObjectFrom(objectName, sitesConfigs[neId][objectName].target, "INFRASTRUCTURE", neId));
              }

              // NOTE:
              //   Operations "merge", and "remove" will not be reverted back!
              //   Operations "create", and "delete" should not be used (not reverted back either)!
            }
            
            if (Object.keys(sitesCleanups[neId]).length === 0)
              delete sitesCleanups[neId];
            
          } else {
            if (neId in this.#deviceCache) {
              logger.error("Deployment on {} ({}) failed with {}", this.#deviceCache[neId], neId, result.errmsg);
              syncErrors.push("[site: "+this.#deviceCache[neId]+", "+neId+"] "+result.errmsg);
            } else {
              logger.error("Deployment on {} failed with {}", neId, result.errmsg);
              syncErrors.push("[site: "+neId+"] "+result.errmsg);
            }
            
            // RESTCONF YANG PATCH failed
            //  - Keep siteCleanups (extraData) for this site to enable housekeeping
            //  - Generate topology from siteCleanup (same content as it was before)
            
            if (neId in sitesCleanups) {
              for (const objectName in sitesCleanups[neId]) {
                topologyObjects.push(topologyFactory.createTopologyObjectFrom(objectName, sitesCleanups[neId][objectName].target, "INFRASTRUCTURE", neId));
              }
            }
          }
          
          if (topology === null)
            topology = topologyFactory.createServiceTopology();

          let xtrainfo = topologyFactory.createTopologyXtraInfoFrom("sitesCleanups", JSON.stringify(sitesCleanups));

          topology.setXtraInfo([xtrainfo]);
          topology.setTopologyObjects(topologyObjects);
        }
      }

      syncResult.setTopology(topology);
    } catch (err) {
      syncErrors.push(err.message);
    }
  
    if (syncErrors.length > 0) {
      syncResult.setSuccess(false);
      syncResult.setErrorCode("500");
      syncResult.setErrorDetail(syncErrors.join('; '));    
    } else {
      syncResult.setSuccess(true);
      if (state === 'delete')
        this.#logic.freeResources(target, config);
    }

    const duration = Date.now()-startTS;
    logger.info("IntentHandler::synchronize() finished within {} ms", duration|0);
    
    return syncResult;      
  }

  /**
    * Function to audit intents. Renders the desired configuration (same
    * as synchronize) and retrieves the actual configuration from MDC.
    * Compares actual against desired configuration to produce the AuditReport.
    * 
    * @param {} input input provided by intent-engine
    * @returns {AuditReport} audit report
    * 
    **/

  async onAudit(input) {
    const startTS = Date.now();
    const target  = input.getTarget();
    const state   = input.getNetworkState().name();

    logger.info("IntentHandler::onAudit() in state {} ", state);

    const config = JSON.parse(input.getJsonIntentConfiguration())[0][this.#logic.INTENT_ROOT];

    var topology    = input.getCurrentTopology();
    var auditReport = new AuditReport();
    auditReport.setIntentType(this.#logic.INTENT_TYPE);
    auditReport.setTarget(target);

    try {
      // Update device-cache (as needed)
      this.#updateDeviceCache();

      // Recall nodal configuration elements from previous synchronize
      var obsoleted = {};
      if (topology && topology.getXtraInfo()!==null && !topology.getXtraInfo().isEmpty()) {
        topology.getXtraInfo().forEach(item => {
          if (item.getKey() === 'sitesCleanups') {
            obsoleted = JSON.parse(item.getValue());
          }
        });
      }

      if (state === 'active') {
        // Obtain resources from Resource Admin
        // Remind, this is done even if the intent was not synchronized before!
        // Required for getSiteParameters() and getGlobalParameters()
        this.#logic.obtainResources(target, config);
        const global = this.#logic.getGlobalParameters(target, config);

        // Iterate sites to populate/update sitesConfigs per target device
        this.#logic.getSiteParameters(target, config, this.#deviceCache).forEach(site => {
          const neId = site['ne-id'];
          const neInfo = mds.getAllInfoFromDevices(neId);
          const neFamilyTypeRelease = neInfo.get(0).getFamilyTypeRelease();
          const neType = neFamilyTypeRelease.split(':')[0];
          const neVersion = neFamilyTypeRelease.split(':')[1];

          // ensure we've got the user-friendly deviceName
          site['ne-name'] = this.#deviceCache[neId];

          const siteFTL = resourceProvider.getResource(this.#logic.getTemplateName(neId, neType));
          const objects = JSON.parse(utilityService.processTemplate(siteFTL, {'target': target, 'site': site, 'global': global, 'neVersion': neVersion, 'mode': 'audit'}));

          // Audit device configuration
          for (const objectName in objects) {
            if ("config" in objects[objectName]) {
              const result = this.#restconfGetDevice(neId, objects[objectName].config.target+"?content=config");
              if (result.success) {
                let iCfg = objects[objectName].config.value;
                for (const key in iCfg) {
                  iCfg = iCfg[key];
                  break;
                }
                
                let aCfg = result.response;
                for (const key in aCfg) {
                  aCfg = aCfg[key];
                  break;
                }

                if (Array.isArray(aCfg))
                  if (aCfg.length === 0) {
                    // an empty was returned
                    // missing object: is-configured=true, is-undesired=default(false)
                    auditReport.addMisAlignedObject(new MisAlignedObject('/'+objects[objectName].config.target, true, neId));
                    aCfg = null;
                  } else {
                    // Due to the nature of RESTCONF GET, we've received a single entry list
                    // Execute the audit against this single entry
                    aCfg = aCfg[0];
                  }

                if (aCfg)
                  this.#compareConfig(neId, objects[objectName].config.target, aCfg, iCfg, objects[objectName].config.operation, objects[objectName].config.ignoreChildren, auditReport, neId, '');
              }
              else if (result.errmsg === "Not Found") {
                // get failed, because path is not configured
                // missing object: is-configured=true, is-undesired=default(false)
                auditReport.addMisAlignedObject(new MisAlignedObject('/'+objects[objectName].config.target, true, neId));
              } else {
                logger.error("RESTCONF GET failed with {}" + result.errmsg);
                throw new Error("RESTCONF GET failed with " + result.errmsg);
              }

              // Configuration object is still present, remove from obsoleted
              if (neId in obsoleted)
                if (objectName in obsoleted[neId])
                  delete obsoleted[neId][objectName];
            }
          }

          for (const objectName in objects) {
            if ("health" in objects[objectName]) {
              for (const path in objects[objectName].health) {
                const iState = objects[objectName].health[path];
                const result = this.#restconfGetDevice(neId, path);
                if (result.success) {
                  let aState = result.response;
                  for (const key in aState) {
                    aState = aState[key];
                    break;
                  }
                  if (Array.isArray(aState))
                    aState = aState[0];

                  this.#compareState(neId, aState, iState, auditReport, path);
                } 
                else if (result.errmsg === "Not Found") {
                  // get failed, because path is not available
                  // missing state object: is-configured=false, is-undesired=default(false)
                  auditReport.addMisAlignedObject(new MisAlignedObject('/'+path, false, neId));
                } else {
                  logger.error("RESTCONF GET failed with {}", result.errmsg);
                  throw new Error("RESTCONF GET failed with " + result.errmsg);
                }
              }
            }
          }
        });
      }

      // Report undesired objects: is-configured=true, is-undesired=true
      for (const neId in obsoleted)
        for (const objectName in obsoleted[neId])
          auditReport.addMisAlignedObject(new MisAlignedObject('/'+obsoleted[neId][objectName].target, true, neId, true));

      auditReport = this.#resolveAudit(auditReport);
    } catch (err) {
      auditReport.setErrorCode("500");
      auditReport.setErrorDetail(err.message);

      // under review with altiplano-team:
      // auditReport.setSuccess(false);
      throw err;
    }

    const duration = Date.now()-startTS;
    logger.info("IntentHandler::onAudit() finished within {} ms", duration|0);
      
    return auditReport;
  }

  /**
    * Function to compute/retrieve read-only state-attributes.
    * 
    * @param {StateRetrievalInput} input input provided by intent-engine
    * @return {*} State attributes report
    * 
    **/

  getStateAttributes(input) {
    const startTS = Date.now();
    const target  = input.getTarget();
    const state   = input.getNetworkState().name();
    const config = JSON.parse(input.getJsonIntentConfiguration())[0][this.#logic.INTENT_ROOT];

    if (state === "delete")
      return null;

    logger.info("IntentHandler::getStateAttributes() in state {}", state);
    
    // Iterate sites to get indiciators
    let indicators = {};
    this.#logic.getSiteParameters(target, config, this.#deviceCache).forEach(site => {
      const neId = site['ne-id'];
      const neInfo = mds.getAllInfoFromDevices(neId);
      const neFamilyTypeRelease = neInfo.get(0).getFamilyTypeRelease();
      const neType = neFamilyTypeRelease.split(':')[0];
      const neVersion = neFamilyTypeRelease.split(':')[1];

      // ensure we've got the user-friendly deviceName
      site['ne-name'] = this.#deviceCache[neId];
      
      const global  = this.#logic.getGlobalParameters(target, config);
      const siteFTL = resourceProvider.getResource(this.#logic.getTemplateName(neId, neType));
      const objects = JSON.parse(utilityService.processTemplate(siteFTL, {'target': target, 'site': site, 'global': global, 'neVersion': neVersion, 'mode': 'state'}));
        
      for (const objectName in objects) {
        if ("indicators" in objects[objectName]) {
          for (const uri in objects[objectName].indicators) {
            const result = this.#restconfGetDevice(neId, uri);
            
            if (result.success) {
              let response = result.response;
              for (const key in response) {
                response = response[key];
                break;
              }
              if (Array.isArray(response))
                response = response[0];

              for (const indicator in objects[objectName].indicators[uri]) {
                const value = this.#jsonPath(response, objects[objectName].indicators[uri][indicator].path);
                if (value && (value.length > 0)) {
                  if (!(indicator in indicators))
                    indicators[indicator] = {};
                  indicators[indicator][neId] = value[0];
                }
              }
            }
          }
        }
      }
    });
    const stateinfo = this.#logic.getState(target, config, input.getCurrentTopology());

    if (!indicators && !stateinfo) {
      logger.info('Neither indicators nor state info collected.');

      const duration = Date.now()-startTS;
      logger.info("IntentHandler::getStateAttributes() finished within {} ms", duration|0);
      return null;
    }

    if (indicators)
      logger.info('collected indicators: '+JSON.stringify(indicators, null, "  "));
    if (stateinfo)
      logger.info('collected state-info: '+JSON.stringify(stateinfo, null, "  "));    
    
    const stateFTL = resourceProvider.getResource("state.ftl");
    const stateXML = utilityService.processTemplate(stateFTL, {'state': stateinfo, 'indicators': indicators});

    logger.info('state report:\n'+stateXML);

    const duration = Date.now()-startTS;
    logger.info("IntentHandler::getStateAttributes() finished within {} ms", duration|0);

    return stateXML;
  }

  /**
    * Returns list of target devices
    * @param {*} input
    * @returns {ArrayList}
    * 
    **/

  getTargettedDevices(input) {
    const startTS = Date.now();
    const target = input.getTarget();
    const config = JSON.parse(input.getJsonIntentConfiguration())[0][this.#logic.INTENT_ROOT];

    // const state    = input.getNetworkState().toString();
    // const version  = input.getIntentTypeVersion();
    // const topology = input.getCurrentTopology();

    logger.info("IntentHandler::getTargettedDevices()");

    let deviceList = new ArrayList();
    this.#logic.getSites(target, config).forEach(neId => deviceList.add(neId));

    const duration = Date.now()-startTS;
    logger.info("IntentHandler::getTargettedDevices() finished within {} ms", duration|0);

    return deviceList;
  }
}