/********************************************************************************
 * INTENT-TYPE BLUEPRINT
 *   use-case: TWAMP light session between two 7x50 routers (system-ip)
 * 
 * (c) 2024 by Nokia
 ********************************************************************************/

import { IntentLogic }   from 'common/IntentLogic.mjs';
import { IntentHandler } from 'common/IntentHandler.mjs';

class OAMConfig extends (IntentLogic) {
  static INTENT_TYPE = 'oamtest';
  static INTENT_ROOT = 'oamtest:oamtest';

  static getSites(target, config) {
    return [config['endpoint-a'], config['endpoint-b']];
  }

  static validate(target, config, contextualErrorJsonObj) {
    if (config['endpoint-a'] === config['endpoint-b'])
      contextualErrorJsonObj['Value inconsistency'] = 'endpoints must be different devices!';
  }

  static getSiteParameters(target, config, siteNames) {
    const sites = [
      {
        'ne-id': config['endpoint-a'],
        'ne-name': siteNames[config['endpoint-a']]
      },
      {
        'ne-id': config['endpoint-b'],
        'ne-name': siteNames[config['endpoint-b']]
      }
    ];

    sites[0]['peer'] = sites[1]; // remote info is required for OAM far-end
    sites[1]['peer'] = sites[0]; // remote info is required for OAM far-end

    return sites;
  }
}

new IntentHandler(OAMConfig);