/********************************************************************************
 * INTENT LOGIC MASTER
 * 
 * (c) 2024 by Nokia
 ********************************************************************************/

export class IntentLogic {
    static INTENT_TYPE = '##'; 
    static INTENT_ROOT = '##:##';

    /**
      * Produces a list of sites (neId: string) to be configured.
      * 
      * Default implementation returns the target, assuming intents for
      * configuring a single site, typically used for any sort of golden
      * site-level configuration.
      * 
      * @param {string} target Intent target
      * @param {object} config Intent configuration (dict)
      * @returns {string[]} List of sites (ne-id) to be configured
      * 
      **/

    static getSites(target, config) {
        return [target];
    }
    
    /**
     * Produces a list of sites, while each site entry is an object (dict)
     * of site-level parameters used to render the corresponding Freemarker
     * template (ftl).
     * 
     * Every site object must have the `ne-id` property, which is used
     * as unique key to drive deployments and audits.
     * 
     * Within the template all properties can be accessed using
     * the expression ${site.parameter}. For example one can extract
     * the site-id using the expression ${site.ne\-id}.
     * 
     * For global parameters (not specific per site), please use the
     * method `getGlobalParameters()`.
     * 
     * If site-level attributes are calculated or retrieved from other sources,
     * for example inventory lookups or resource administrator, here is the place
     * to put the corresponding logic. For resource allocation (obtain/release)
     * there are dedicated methods available.
     * 
     * Default implementation returns a single entry list, assuming intents
     * for configuring a single site, typically used for any sort of golden
     * site-level configuration. The single entry is the intent config itself
     * while `ne-id` and `ne-name` are inserted (from target).
     * 
     * @param {string} target Intent target
     * @param {Dict}   config Intent configuration
     * @param {Dict}   siteNames Used to translate siteId to siteNames (w/o API calls)
     * @returns {Dict} site-level settings (site.*)
     */

    static getSiteParameters(target, config, siteNames) {
        config['ne-id'] = target;
        config['ne-name'] = siteNames[target];
        return [config];
    }

    /**
     * Produces an object (dict) of intent-level parameters (valid for all sites).
     * 
     * Within the template all properties can be accessed using
     * the expression ${global.parameter}.
     * 
     * If intent-level attributes are calculated or retrieved from other sources,
     * for example inventory lookups or resource administrator, here is the place
     * to put the corresponding logic. For resource allocation (obtain/release)
     * there is dedicated methods available.
     * 
      * Default implementation returns the config, assuming intents for
      * configuring a single site, typically used for any sort of golden
      * site-level configuration.
     *
     * @param {string} target Intent target
     * @param {Dict}   config Intent configuration
     * @returns {Dict} intent-level settings (global.*)
     */

    static getGlobalParameters(target, config) {
        return config;
    }    

    /**
     * Intent-type specific validation. It will be executed in addition to framework-level
     * validations. Default implementation does not have any extra validation rules.
     * 
     * @param {string} target Intent target
     * @param {Dict}   config Intent configuration
     * @param {Dict} contextualErrorJsonObj used to return list of validation errors (key/value pairs)
     */

    static validate(target, config, contextualErrorJsonObj) {
    }

    /**
     * Migrate from/to a different versions of this intent-type.
     * Method supports upgrades to this version and downgrades from this version.
     * 
     * WARNING:
     * This is a placeholder for now!
     * Implementation and examples will be made available soon.
     * 
     * @param {object} migrationInput object that has the migration input
     * 
     */

    static migrate(migrationInput) {
        let sourceVersion = parseInt(migrationInput.getSourceVersion());
        let targetVersion = parseInt(migrationInput.getTargetVersion());
        let intentConfigJson = JSON.parse(migrationInput.getJsonIntentConfiguration())[0][this.modelRoot];
        let intentTopology = migrationInput.getCurrentTopology();
        return '';
    }
 
    /**
     * Produces an object with all state attributes to render `state.ftl`
     * Default implementation returns Dict without entries.
     *
     * @param {string} target Intent target
     * @param {Dict}   config Intent configuration
     * @param {Dict}   topology Intent topology
     * @returns {Dict} state attributes
     */

    static getState(target, config, topology) {    
        return {};
    }

    /**
     * Obtain resources from resource administrator (or external).
     * Called if intent moves into planned/deployed state to ensure resources are available.
     *
     * @param {string} target Intent target
     * @param {Dict}   config Intent configuration
     */

    static obtainResources(target, config) {
    }

    /**
     * Releases resources from resource administrator (or external).
     * Called if intent moves into 'not present' state to ensure resources are released.
     *
     * @param {string} target Intent target
     * @param {Dict}   config Intent configuration
     */

    static freeResources(target, config) {
    }
  
    /**
      * Returns the name of free-marker template (ftl) to be used (specific per site).
      * Generic recommendation is to use a common pattern like '{neType}.ftl'
      *
      * NOTE:
      *   In some cases we need to understand the role of a node like hub-site, server-site,
      *   switching-site. This may require that getSites returns the sites and roles and roles
      *   would need to be passed into this method.
      * 
      * @param {} neId
      * @param {} familyTypeRelease
      * @returns {String} name of the FTL file
      */

    static getTemplateName(neId, familyTypeRelease) {
        const neType = familyTypeRelease.split(':')[0];
    
        switch (neType) {
            case '7220 IXR SRLinux':
            case '7250 IXR SRLinux':
            case '7730 SXR SRLinux':
                return 'SRLinux.ftl';
            case '7750 SR':
            case '7450 ESS':
            case '7950 XRS':
            case '7250 IXR':
                return 'SR OS.ftl';
            default:
                return 'OpenConfig.ftl';
        }
    }
}