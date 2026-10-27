{* Este DIV se usa para mostrar los mensajes de información *}
<div
    id="issabel-module-info-message"
    class="iss-alert iss-alert--info"
    role="status"
    style="display: none;">
    <div class="iss-alert__content">
        <span id="issabel-module-info-message-text"></span>
    </div>
</div>
{* Este DIV se usa para mostrar los mensajes de error *}
<div
    id="issabel-module-error-message"
    class="iss-alert iss-alert--error"
    role="alert"
    style="display: none;">
    <div class="iss-alert__content">
        <span id="issabel-module-error-message-text"></span>
    </div>
</div>
<div id="endpointConfigApplication" class="iss-endpointconfig">

<script type="text/x-handlebars" data-template-name="loading">
<div style="text-align: center; padding: 40px;"><i class="ti ti-loader" aria-hidden="true"></i></div>
</script>

<script type="text/x-handlebars" data-template-name="endpoints">
  <div class="neo-endpointconfig-header-row">
    {literal}
    {{#view
        style="cursor:default" }}
        {{#if scanInProgress }}
            <div class="neo-table-header-row-filter">
                <i class="ti ti-loader" aria-hidden="true"></i>
                <button type="button" class="neo-table-action" {{action "scanCancel"}} >{/literal}{$LBL_CANCEL}{literal}</button>
            </div>
        {{else}}
            {{#unless uiblock}}
                <div class="neo-table-header-row-filter" title="{/literal}{$LBL_SCAN}{literal}">
                    {{view App.NetmaskView valueBinding="scanMask" placeholder="192.168.1.0/24" }}
                    <button type="button" class="neo-table-action" title="{/literal}{$LBL_SCAN}{literal}" aria-label="{/literal}{$LBL_SCAN}{literal}" {{action "scanStart"}} ><i class="ti ti-search" aria-hidden="true"></i></button>
                    {{#if scanMaskError}}<div class="invalid-feedback d-block">{{scanMaskError}}</div>{{/if}}
                </div>
            {{/unless}}
        {{/if}}
        {{#if configInProgress }}
            <div class="neo-table-header-row-filter">
                {/literal}{$LBL_STEP}{literal} {{completedsteps}} {/literal}{$of}{literal} {{totalsteps}} {{#if founderror}}{/literal}{$LBL_WITH_ERRORS}{literal}{{/if}}
            </div>
            <div class="neo-table-header-row-filter" style="width: 600px;">
            {{view App.ConfigProgressView valueBinding="completedsteps" maxBinding="totalsteps" }}
            </div>
        {{else}}
	        {{#unless uiblock }}
	            <div class="neo-table-header-row-filter" title="{/literal}{$TOOLTIP_CONFIGURE}{literal}" {{action "configStart"}} >
	                <button type="button" class="neo-table-action" title="{/literal}{$TOOLTIP_CONFIGURE}{literal}" aria-label="{/literal}{$TOOLTIP_CONFIGURE}{literal}"><i class="ti ti-phone-incoming" aria-hidden="true"></i></button>
	            </div>
	        {{/unless}}
        {{/if}}
        {{#unless uiblock }}
            {{#linkTo "endpoints.getconfiglog"}}
            <div class="neo-table-header-row-filter" title="{/literal}{$LBL_VIEW_LOG}{literal}">
                <button type="button" class="neo-table-action" title="{/literal}{$LBL_VIEW_LOG}{literal}" aria-label="{/literal}{$LBL_VIEW_LOG}{literal}"><i class="ti ti-file-text" aria-hidden="true"></i></button>
            </div>
            {{/linkTo}}
        {{/unless}}
        {{#if unsetInProgress }}
            <div class="neo-table-header-row-filter">
                <i class="ti ti-loader" aria-hidden="true"></i>
            </div>
        {{else}}
	        {{#unless uiblock }}
	            <div class="neo-table-header-row-filter" title="{/literal}{$LBL_FORGET}{literal}" {{action "forgetSelected"}} >
	                <button type="button" class="neo-table-action" title="{/literal}{$LBL_FORGET}{literal}" aria-label="{/literal}{$LBL_FORGET}{literal}"><i class="ti ti-trash" aria-hidden="true"></i></button>
	            </div>
	        {{/unless}}
        {{/if}}
        {{#unless uiblock }}
            {{#view App.SubMenuView}}
                <div class="neo-table-header-row-filter" title="{/literal}{$LBL_DOWNLOAD}{literal}" {{action "toggleMenu" target="view"}}>
                <button type="button" class="neo-table-action" title="{/literal}{$LBL_DOWNLOAD}{literal}" aria-label="{/literal}{$LBL_DOWNLOAD}{literal}"><i class="ti ti-download" aria-hidden="true"></i></button>
                </div>
                <div class="neo-endpointconfig-submenu" {{bindAttr style="view.menuStyle"}}>
                    <a href="?menu={/literal}{$module_name}{literal}&amp;action=download&amp;rawmode=yes&amp;format=legacy">
                    <i class="ti ti-file-spreadsheet" aria-hidden="true"></i>&nbsp;{/literal}{$LBL_CSV_LEGACY}{literal}
                    </a>
                    <a href="?menu={/literal}{$module_name}{literal}&amp;action=download&amp;rawmode=yes&amp;format=xml">
                    <i class="ti ti-file-code" aria-hidden="true"></i>&nbsp;{/literal}{$LBL_XML}{literal}
                    </a>
                    <a href="?menu={/literal}{$module_name}{literal}&amp;action=download&amp;rawmode=yes&amp;format=nested">
                    <i class="ti ti-file-spreadsheet" aria-hidden="true"></i>&nbsp;{/literal}{$LBL_CSV_NESTED}{literal}
                    </a>
                </div>
            {{/view}}
            {{#view App.SubMenuView}}
                <div class="neo-table-header-row-filter" title="{/literal}{$LBL_UPLOAD}{literal}" {{action "toggleMenu" target="view"}}>
                <button type="button" class="neo-table-action" title="{/literal}{$LBL_UPLOAD}{literal}" aria-label="{/literal}{$LBL_UPLOAD}{literal}"><i class="ti ti-upload" aria-hidden="true"></i></button>
                </div>
                <div class="neo-endpointconfig-submenu" {{bindAttr style="view.menuStyleManual"}}>
                    {{#if fileUploadSupported}}
	                    {{view App.EndpointUploadView }}
	                    {{#if uploadInProgress }}
	                    {{view JQ.ProgressBar valueBinding="completedupload" maxBinding="totalupload" }}
	                    {{/if}}
                    {{else}}
                        <form method="POST" action="?" enctype="multipart/form-data">
                            {/literal}{$ISSABEL_CSRF_FIELD}{literal}
                            <input type="hidden" name="module" value="{/literal}{$module_name}{literal}" />
                            <input type="hidden" name="action" value="upload" />
                            <input type="file" name="endpointfile[]" />
                            <input type="submit" class="btn btn-primary btn-sm" name="legacyupload" value="{/literal}{$LBL_UPLOAD}{literal}" />
                        </form>
                    {{/if}}
                </div>
            {{/view}}
        {{/unless}}
    {{/view}}{/literal}
    {literal}{{view App.NeoNavigationView }}{/literal}
  </div>
<div id="addonlist" class="iss-grid">

<table class="table iss-table" align="center" cellspacing="0" cellpadding="0" width="100%">
<thead>
<tr class="neo-table-title-row">
    <th scope="col" class="neo-table-title-row">{literal}{{view Ember.Checkbox checkedBinding="seleccionTodos" aria-label="{/literal}{$LBL_SELECT_ALL}{literal}"}}{/literal}&nbsp;</th>
    <th scope="col" class="neo-table-title-row">{$LBL_STATUS}</th>
    <th scope="col" class="neo-table-title-row">{$LBL_MAC_ADDRESS}</th>
    <th scope="col" class="neo-table-title-row">{$LBL_CURRENT_IP}</th>
    <th scope="col" class="neo-table-title-row">{$LBL_MANUFACTURER}</th>
    <th scope="col" class="neo-table-title-row">{$LBL_MODEL}</th>
    <th scope="col" class="neo-table-title-row">{$LBL_OPTIONS}</th>
</tr>
</thead>

{literal}{{#view tagName="tbody"}}
{{#each endpoint in content}}
<tr class="neo-table-data-row">
	<td class="neo-table-data-row">{{view Ember.Checkbox checkedBinding="endpoint.isSelected" aria-label="{/literal}{$LBL_SELECT_ENDPOINT}{literal}"}}</td>
    <td class="neo-table-data-row">
    {{#if endpoint.isFromBatch}}<span class="iss-endpointconfig-flag" title="{/literal}{$TOOLTIP_FROM_BATCH}{literal}"><i class="ti ti-file-import" aria-hidden="true"></i></span>{{/if}}
    {{#if endpoint.isModified}}<span class="iss-endpointconfig-flag" title="{/literal}{$TOOLTIP_MODIFIED}{literal}"><i class="ti ti-device-floppy" aria-hidden="true"></i></span>{{/if}}
    {{#if endpoint.hasExtensions}}<span class="iss-endpointconfig-flag" title="{/literal}{$TOOLTIP_HAS_EXTENSIONS}{literal}"><i class="ti ti-user" aria-hidden="true"></i></span>{{/if}}
    {{#if endpoint.is_missing}}<span class="iss-endpointconfig-flag text-danger" title="{/literal}{$TOOLTIP_MISSING}{literal}"><i class="ti ti-alert-triangle" aria-hidden="true"></i></span>{{/if}}
    </td>
    <td class="neo-table-data-row">{{endpoint.mac_address}}</td>
    <td class="neo-table-data-row">{{#if endpoint.last_known_ipv4}}<a target="_blank" {{bindAttr href="endpoint.adminUrl"}}>{{endpoint.last_known_ipv4}}</a>{{else}}{/literal}{$LBL_UNKNOWN}{literal}{{/if}}</td>
	<td class="neo-table-data-row">{{endpoint.name_manufacturer}}</td>
	<td class="neo-table-data-row">{{view Ember.Select
	    contentBinding="endpoint.modelSelect"
	    optionValuePath="content.id_model"
        optionLabelPath="content.name_model"
        valueBinding="endpoint.id_model"
        disabledBinding="scanInProgress"}}</td>
    <td class="neo-table-data-row">
        {{#linkTo "endpoints.endpointconfig" endpoint }}[{/literal}{$LBL_CONFIGURE}{literal} {{endpoint.last_known_ipv4}}]{{/linkTo}}
    </td>
</tr>
{{else}}
<tr class="neo-table-data-row">
    <td class="neo-table-data-row iss-empty" colspan="7"><i class="ti ti-device-desktop-off" aria-hidden="true"></i>{/literal}{$MSG_NO_ENDPOINTS}{literal}</td>
</tr>
{{/each}}
{{/view}}{/literal}
</table>

</div>
<div id="footer" class="iss-grid__footer">
{literal}{{view App.NeoNavigationView }}{/literal}
</div>

{literal}{{outlet}}{/literal}
</script>

<script type="text/x-handlebars" data-template-name="endpoints/endpointconfig">
<div
    id="issabel-module-error-message-dialog"
    class="iss-alert iss-alert--error"
    role="alert"
    style="display: none;">
    <div class="iss-alert__content">
        <span id="issabel-module-error-message-text-dialog"></span>
    </div>
</div>
{literal}{{outlet}}{/literal}
</script>

<script type="text/x-handlebars" data-template-name="endpoints/getconfiglog">
{literal}
{{view App.FullTextArea
    valueBinding="log"
    disabled="disabled"}}
{/literal}
</script>

<script type="text/x-handlebars" data-template-name="neo-navigation">
    <span class="iss-grid__nav-arrow" {literal}{{action "displayStart"}}{/literal} title="{$lblStart}" aria-label="{$lblStart}"><i class="ti ti-chevrons-left" aria-hidden="true"></i></span>
    <span class="iss-grid__nav-arrow" {literal}{{action "displayPrevious" }}{/literal} title="{$lblPrevious}" aria-label="{$lblPrevious}"><i class="ti ti-chevron-left" aria-hidden="true"></i></span>
    ({$showing} {literal}{{startPosition}} - {{endPosition}}{/literal} {$of} <span>{literal}{{completeList.length}}{/literal}</span>)
    <span class="iss-grid__nav-arrow" {literal}{{action "displayNext"}}{/literal} title="{$lblNext}" aria-label="{$lblNext}"><i class="ti ti-chevron-right" aria-hidden="true"></i></span>
    <span class="iss-grid__nav-arrow" {literal}{{action "displayEnd"}}{/literal} title="{$lblEnd}" aria-label="{$lblEnd}"><i class="ti ti-chevrons-right" aria-hidden="true"></i></span>
</script>
</div>

<script type="text/javascript">
var lastop_error_message = {$LASTOP_ERROR_MESSAGE};
var arrLang_main = {$ARRLANG_MAIN};
</script>
