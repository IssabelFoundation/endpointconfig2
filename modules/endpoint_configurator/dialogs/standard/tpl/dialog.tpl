<script type="text/x-handlebars" data-template-name="endpointconfig-standard">
    <ul>
        <li><a href="#endpointconfig-standard-information">{$DIALOG_STANDARD_TITLE_INFORMATION}</a></li>
        <li><a href="#endpointconfig-standard-accounts">{$DIALOG_STANDARD_TITLE_ACCOUNTS}</a></li>
        <li><a href="#endpointconfig-standard-network">{$DIALOG_STANDARD_TITLE_NETWORK}</a></li>
        <li><a href="#endpointconfig-standard-credentials">{$DIALOG_STANDARD_TITLE_CREDENTIALS}</a></li>
        <li><a href="#endpointconfig-standard-endpointproperties">{$DIALOG_STANDARD_TITLE_PROPERTIES}</a></li>
    </ul>
    <div id="endpointconfig-standard-information" class="iss-form">
        <div class="iss-formgrid iss-formgrid--3col iss-formgrid--readonly">
            <div class="iss-field">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_MANUFACTURER}</span>
                <span class="iss-field__control iss-field__value">{literal}{{name_manufacturer}}{/literal}</span>
            </div>
            <div class="iss-field">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_MODEL}</span>
                <span class="iss-field__control iss-field__value">{literal}{{#if modelObj.name_model}}{{modelObj.name_model}} ({{modelObj.description}}){{else}}{/literal}{$DIALOG_STANDARD_LBL_UNKNOWN_MODEL}{literal}{{/if}}{/literal}</span>
            </div>
            <div class="iss-field">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_MAX_SIP_ACCOUNTS}</span>
                <span class="iss-field__control iss-field__value">{literal}{{#if details}}{{details.max_sip_accounts}}{{else}}{/literal}{$DIALOG_STANDARD_LBL_UNKNOWN}{literal}{{/if}}{/literal}</span>
            </div>
            <div class="iss-field">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_MAX_IAX2_ACCOUNTS}</span>
                <span class="iss-field__control iss-field__value">{literal}{{#if details}}{{details.max_iax2_accounts}}{{else}}{/literal}{$DIALOG_STANDARD_LBL_UNKNOWN}{literal}{{/if}}{/literal}</span>
            </div>
            <div class="iss-field">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_MAC}</span>
                <span class="iss-field__control iss-field__value">{literal}{{mac_address}}{/literal}</span>
            </div>
            <div class="iss-field">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_CURRENT_IP}</span>
                <span class="iss-field__control iss-field__value">{literal}{{#if last_known_ipv4 }}{{last_known_ipv4}}{{else}}{/literal}{$DIALOG_STANDARD_LBL_UNKNOWN}{literal}{{/if}}{/literal}</span>
            </div>
            <div class="iss-field" title="{$DIALOG_STANDARD_TOOLTIP_DYNIP}">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_DYNIP}</span>
                <span class="iss-field__control iss-field__value">{literal}{{#if modelObj}}{{#if modelObj.dynamic_ip_supported}}{/literal}{$DIALOG_STANDARD_LBL_YES}{literal}{{else}}{/literal}{$DIALOG_STANDARD_LBL_NO}{literal}{{/if}}{{else}}{/literal}{$DIALOG_STANDARD_LBL_UNKNOWN}{literal}{{/if}}{/literal}</span>
            </div>
            <div class="iss-field" title="{$DIALOG_STANDARD_TOOLTIP_STATICIP}">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_STATICIP}</span>
                <span class="iss-field__control iss-field__value">{literal}{{#if modelObj}}{{#if modelObj.static_ip_supported}}{/literal}{$DIALOG_STANDARD_LBL_YES}{literal}{{else}}{/literal}{$DIALOG_STANDARD_LBL_NO}{literal}{{/if}}{{else}}{/literal}{$DIALOG_STANDARD_LBL_UNKNOWN}{literal}{{/if}}{/literal}</span>
            </div>
            <div class="iss-field" title="{$DIALOG_STANDARD_TOOLTIP_VLAN}">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_VLAN}</span>
                <span class="iss-field__control iss-field__value">{$DIALOG_STANDARD_LBL_UNIMPLEMENTED}</span>
            </div>
            <div class="iss-field" title="{$DIALOG_STANDARD_TOOLTIP_STATICPROV}">
                <span class="iss-field__label">{$DIALOG_STANDARD_LBL_STATICPROV}</span>
                <span class="iss-field__control iss-field__value">{literal}{{#if modelObj}}{{#if modelObj.static_prov_supported}}{/literal}{$DIALOG_STANDARD_LBL_YES}{literal}{{else}}{/literal}{$DIALOG_STANDARD_LBL_NO}{literal}{{/if}}{{else}}{/literal}{$DIALOG_STANDARD_LBL_UNKNOWN}{literal}{{/if}}{/literal}</span>
            </div>
        </div>
    </div>
    <div id="endpointconfig-standard-accounts" class="iss-form">
        <table class="iss-endpointconfig-accounts" width="100%">
        <thead>
            <tr>
                <th scope="col">{$DIALOG_STANDARD_UNASSIGNED_ACCOUNTS} ({literal}{{App.accountsController.length}}{/literal})</th>
                <th scope="col">{$DIALOG_STANDARD_ASSIGNED_ACCOUNTS} ({literal}{{details.accountsController.length}}{/literal})</th>
            </tr>
        </thead>
        <tbody><tr>
        {literal}
        <td valign="top" width="50%">
            {{#view App.StandardUnboundAccountsView controllerBinding="App.accountsController"}}
            {{#each controller}}
                <li {{bindAttr id="idattr"}} {{action "selectAccount" this }} >
                    {{#if priority}}{{priority}}: {{/if}}{{tech}}/{{account}} ({{extension}}) - {{description}}
                    {{#if registerip}}<br/><span class="text-danger" title="{/literal}{$DIALOG_STANDARD_TOOLTIP_REGISTERED}{literal}">{/literal}{$DIALOG_STANDARD_LBL_REGISTERED_AT}{literal}: {{registerip}}</span>{{/if}}
                </li>
            {{/each}}
            {{/view}}
        </td>
        <td valign="top" >
            <table width="100%"><tbody><tr><td>
            {{#view App.StandardBoundAccountsView controllerBinding="details.accountsController"}}
            {{#each controller}}
                <li {{bindAttr id="idattr"}} {{action "selectAccount" this }} >
                    {{#if priority}}{{priority}}: {{/if}}{{tech}}/{{account}} ({{extension}}) - {{description}}
                    {{#if registerip}}<br/><span class="text-danger" title="{/literal}{$DIALOG_STANDARD_TOOLTIP_REGISTERED}{literal}">{/literal}{$DIALOG_STANDARD_LBL_REGISTERED_AT}{literal}: {{registerip}}</span>{{/if}}
                </li>
            {{/each}}
            {{/view}}
            </td></tr>
            <tr><td>
            {{#if details.accountsController.selectedAccount}}
                {{#with details.accountsController.selectedAccount}}
                <b>{/literal}{$DIALOG_STANDARD_LBL_PROPERTIES}{literal} {{tech}}/{{account}} ({{extension}}) - {{description}}</b>
                {{view App.EndpointconfigPropertylistView controllerBinding="propertiesController" }}
                {{/with}}
            {{else}}
                {/literal}{$DIALOG_STANDARD_LBL_NOACCOUNTS}{literal}
            {{/if}}
            </td></tr>
            </tbody></table>
        </td>
        {/literal}
        </tr>
        </tbody></table>
    </div>
    <div id="endpointconfig-standard-network" class="iss-form">
        <div class="iss-inline-field">
            {literal}
            <input value="1" id="networktype-isDHCP" type="radio" name="networktype" {{action "setDHCP" on="change"}} {{bindAttr checked="isDHCP"}} />
            <label for="networktype-isDHCP">{/literal}{$DIALOG_STANDARD_LBL_DYNIP}{literal}</label>
            <input value="0" id="networktype-isStatic" type="radio" name="networktype" {{action "setStatic" on="change"}} {{bindAttr checked="isStatic"}} />
            <label for="networktype-isStatic">{/literal}{$DIALOG_STANDARD_LBL_STATICIP}{literal}</label>
            {/literal}
        </div>
        {literal}{{#if isStatic}}{/literal}
        <div class="iss-form__hint"><span class="iss-required">*</span> {$DIALOG_STANDARD_LBL_REQUIRED_FIELD}</div>
        <section class="iss-card">
            <div class="iss-card__header"><i class="ti ti-network" aria-hidden="true"></i> {$DIALOG_STANDARD_LBL_STATIC_NETATTR}</div>
            <div class="iss-card__body iss-formgrid">
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_STATIC_IP}&nbsp;<span class="iss-required">*</span></span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="static_ip" placeholderBinding="last_known_ipv4" valueBinding="details.static_ip"}}{/literal}</span>
                    {literal}{{#if details.errors.static_ip}}<div class="invalid-feedback d-block">{{details.errors.static_ip}}</div>{{/if}}{/literal}
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_STATIC_NETMASK}&nbsp;<span class="iss-required">*</span></span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="static_mask" placeholder="255.255.255.0" valueBinding="details.static_mask"}}{/literal}</span>
                    {literal}{{#if details.errors.static_mask}}<div class="invalid-feedback d-block">{{details.errors.static_mask}}</div>{{/if}}{/literal}
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_STATIC_GW}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="static_gw" placeholder="192.168.0.1" valueBinding="details.static_gw"}}{/literal}</span>
                    {literal}{{#if details.errors.static_gw}}<div class="invalid-feedback d-block">{{details.errors.static_gw}}</div>{{/if}}{/literal}
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_STATIC_DNS1}&nbsp;<span class="iss-required">*</span></span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="static_dns1" placeholder="8.8.8.8" valueBinding="details.static_dns1"}}{/literal}</span>
                    {literal}{{#if details.errors.static_dns1}}<div class="invalid-feedback d-block">{{details.errors.static_dns1}}</div>{{/if}}{/literal}
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_STATIC_DNS2}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="static_dns2" placeholder="8.8.4.4" valueBinding="details.static_dns2"}}{/literal}</span>
                    {literal}{{#if details.errors.static_dns2}}<div class="invalid-feedback d-block">{{details.errors.static_dns2}}</div>{{/if}}{/literal}
                </div>
            </div>
        </section>
        {literal}{{/if}}{/literal}
    </div>
    <div id="endpointconfig-standard-credentials" class="iss-form">
        <section class="iss-card">
            <div class="iss-card__header"><i class="ti ti-key" aria-hidden="true"></i> {$DIALOG_STANDARD_TITLE_CREDENTIALS}</div>
            <div class="iss-card__body iss-formgrid">
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_TELNET_USER}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="telnet_username" valueBinding="details.telnet_username"}}{/literal}</span>
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_TELNET_PASS}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="telnet_password" type="password" valueBinding="details.telnet_password"}}{/literal}</span>
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_HTTP_USER}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="http_username" valueBinding="details.http_username"}}{/literal}</span>
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_HTTP_PASS}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="http_password" type="password" valueBinding="details.http_password"}}{/literal}</span>
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_SSH_USER}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="ssh_username" valueBinding="details.ssh_username"}}{/literal}</span>
                </div>
                <div class="iss-field">
                    <span class="iss-field__label">{$DIALOG_STANDARD_SSH_PASS}</span>
                    <span class="iss-field__control">{literal}{{view App.IssabelEndpointTextField elementId="ssh_password" type="password" valueBinding="details.ssh_password"}}{/literal}</span>
                </div>
            </div>
        </section>
    </div>
    <div id="endpointconfig-standard-endpointproperties" class="iss-form">
        <p class="iss-field__help">{$DIALOG_STANDARD_PROPERTIES_MESSAGE}</p>
        {literal}{{view App.EndpointconfigPropertylistView controllerBinding="details.endpointPropertiesController" }}{/literal}
    </div>
</script>
<script type="text/x-handlebars" data-template-name="endpointconfig-propertylist">
    <table cellspacing="0" cellpadding="0" class="table iss-table iss-mini-table">
    <thead>
		<tr class="neo-table-title-row">
		    <th scope="col" class="neo-table-title-row">{$DIALOG_STANDARD_LBL_PROPERTY}</th>
		    <th scope="col" class="neo-table-title-row">{$DIALOG_STANDARD_LBL_VALUE}</th>
		    <th scope="col" class="neo-table-title-row"><span class="visually-hidden">{$DIALOG_STANDARD_LBL_ACTIONS}</span></th>
		</tr>
    </thead>
    <tbody>
    {literal}
    {{#each controller }}
    <tr class="neo-table-data-row">
        <td class="neo-table-data-row"><b>{{key}}:</b></td>
        <td class="neo-table-data-row">{{view App.IssabelEndpointTextField valueBinding="value"}}</td>
        <td class="neo-table-data-row">{{view App.DeletePropertyButtonView label="-" propkeyBinding="key"}}</td>
    </tr>
    {{/each}}
    <tr class="neo-table-data-row">
        <td class="neo-table-data-row">{{view App.IssabelEndpointTextField size="20" valueBinding="controller.tempKey"}}</td>
        <td class="neo-table-data-row">{{view App.IssabelEndpointTextField size="20" valueBinding="controller.tempValue"}}</td>
        <td class="neo-table-data-row">{{view App.AddPropertyButtonView label="+"}}</td>
    </tr>
    {/literal}
    </tbody></table>
</script>
