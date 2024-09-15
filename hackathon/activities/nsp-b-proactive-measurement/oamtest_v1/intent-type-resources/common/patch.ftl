<#setting number_format="computer">

<#-- This is generetic templates to render a RFC8072 compliant YANG PATCH body -->

<#-- Input parameters: -->
<#--   patchId = string -->
<#--   patchItems = dict of config elements to patch -->
<#--     key = target path -->
<#--     value:operation = remove | replace -->
<#--     value:value     = payload (string in JSON format) -->
<#--     value:name      = nodal object to be created/updated/deleted -->

{
  "ietf-yang-patch:yang-patch": {
    "patch-id": "${patchId}",
    "edit": [
<#list patchItems as objectName, cfg >
      {
        "edit-id": "${objectName}",
        "target": "${cfg.target}",
<#if cfg.value??>
        "value":  ${cfg.value},
</#if>
        "operation": "${cfg.operation}"
      } <#sep>,
</#list>
    ]
  }
}
