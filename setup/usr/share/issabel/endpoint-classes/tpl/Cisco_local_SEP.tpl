<?xml version="1.0" encoding="UTF-8"?>
<!-- https://usecallmanager.nz -->
<device>
    <fullConfig>true</fullConfig>
    <deviceProtocol>SIP</deviceProtocol>
    <!-- IP address family to use on the phone. 
    0	IPv4	1	IPv6	2	IPv4 and IPv6 -->
    <ipAddressMode>0</ipAddressMode>
    <allowAutoConfig>true</allowAutoConfig>
    <dadEnable>true</dadEnable>
    <redirectEnable>false</redirectEnable>
    <echoMultiEnable>false</echoMultiEnable>
    <!-- Preferred IP address family for signalling.
    0	IPv4	1	IPv6 -->
    <ipPreferenceModeControl>0</ipPreferenceModeControl>
    <ipMediaAddressFamilyPreference>0</ipMediaAddressFamilyPreference>
    <devicePool>
        <dateTimeSetting>
            <dateTemplate>D/M/Y</dateTemplate>
            <!-- https://usecallmanager.nz/sepmac-cnf-xml.html#timeZone -->
            <timeZone>{{time_zone}}</timeZone>
            <ntps>
                <ntp>
                    <name>{{server_ip}}</name>
                    <ntpMode>unicast</ntpMode>
                </ntp>
            </ntps>
        </dateTimeSetting>
        <callManagerGroup>
            <members>
                <member priority="0">
                    <callManager>
                        <!-- <name>IssabelPBX</name> -->
                        <ports>
                            <ethernetPhonePort>2000</ethernetPhonePort>
                            <sipPort>5060</sipPort>
                            <securedSipPort>5061</securedSipPort>
                        </ports>
                        <processNodeName>{{server_ip}}</processNodeName>
                    </callManager>
                </member>
            </members>
        </callManagerGroup>
    </devicePool>
    <!-- Host name or IP address of the server running the Trust Verification Service. -->
    <!-- 
    <TVS>
    <members>
      <member priority="0">
        <port>2445</port>
        <address>{{server_ip}}</address>
      </member>
    </members>
    </TVS> -->
    <!-- 
  <vpnGroup>
    <mtu>1290</mtu>
    <failConnectTime>30</failConnectTime>
    <authMethod>0</authMethod>
    <pswdPersistent>1</pswdPersistent>
    <autoNetDetect>1</autoNetDetect>
    <enableHostIDCheck>0</enableHostIDCheck>
    <addresses>
      <url1></url1>
    </addresses>
    <credentials>
      <hashAlg>0</hashAlg>
      <certHash1></certHash1>
    </credentials>
  </vpnGroup> -->
    <sipProfile>
        <sipProxies>
            <!-- 
      <backupProxy>USECALLMANAGER</backupProxy>
        <backupProxyPort>{{sip[0].server_port}}</backupProxyPort>
        <emergencyProxy>USECALLMANAGER</emergencyProxy>
        <emergencyProxyPort>{{sip[0].server_port}}</emergencyProxyPort>
        <outboundProxy>USECALLMANAGER</outboundProxy>
        <outboundProxyPort>{{sip[0].server_port}}</outboundProxyPort> -->
            <registerWithProxy>true</registerWithProxy>
        </sipProxies>
        <sipCallFeatures>
            <cnfJoinEnabled>true</cnfJoinEnabled>
            <callForwardURI>x-cisco-serviceuri-cfwdall</callForwardURI>
            <callPickupURI>x-cisco-serviceuri-pickup</callPickupURI>
            <callPickupListURI>x-cisco-serviceuri-opickup</callPickupListURI>
            <callPickupGroupURI>x-cisco-serviceuri-gpickup</callPickupGroupURI>
            <meetMeServiceURI>x-cisco-serviceuri-meetme</meetMeServiceURI>
            <abbreviatedDialURI>x-cisco-serviceuri-abbrdial</abbreviatedDialURI>
            <rfc2543Hold>false</rfc2543Hold>
            <callHoldRingback>1</callHoldRingback>
            <localCfwdEnable>true</localCfwdEnable>
            <semiAttendedTransfer>true</semiAttendedTransfer>
            <anonymousCallBlock>0</anonymousCallBlock>
            <callerIdBlocking>0</callerIdBlocking>
            <dndControl>0</dndControl>
            <remoteCcEnable>true</remoteCcEnable>
            <retainForwardInformation>false</retainForwardInformation>
            <uriDialingDisplayPreference>1</uriDialingDisplayPreference>
        </sipCallFeatures>
        <sipStack>
            <sipInviteRetx>6</sipInviteRetx>
            <sipRetx>10</sipRetx>
            <timerInviteExpires>180</timerInviteExpires>
            <timerRegisterExpires>3600</timerRegisterExpires>
            <timerRegisterDelta>5</timerRegisterDelta>
            <timerKeepAliveExpires>120</timerKeepAliveExpires>
            <timerSubscribeExpires>120</timerSubscribeExpires>
            <timerSubscribeDelta>5</timerSubscribeDelta>
            <timerT1>500</timerT1>
            <timerT2>4000</timerT2>
            <maxRedirects>70</maxRedirects>
            <remotePartyID>true</remotePartyID>
            <userInfo>Phone</userInfo>
        </sipStack>
        <autoAnswerTimer>1</autoAnswerTimer>
        <autoAnswerAltBehavior>false</autoAnswerAltBehavior>
        <autoAnswerOverride>true</autoAnswerOverride>
        <transferOnhookEnabled>true</transferOnhookEnabled>
        <enableVad>false</enableVad>
        <preferredCodec>none</preferredCodec>
        <dtmfAvtPayload>101</dtmfAvtPayload>
        <dtmfDbLevel>3</dtmfDbLevel>
        <dtmfOutofBand>avt</dtmfOutofBand>
        <alwaysUsePrimeLine>false</alwaysUsePrimeLine>
        <alwaysUsePrimeLineVoiceMail>false</alwaysUsePrimeLineVoiceMail>
        <kpml>0</kpml>
        <phoneLabel></phoneLabel>
        <stutterMsgWaiting>0</stutterMsgWaiting>
        <callStats>true</callStats>
        <offhookToFirstDigitTimer>15000</offhookToFirstDigitTimer>
        <silentPeriodBetweenCallWaitingBursts>10</silentPeriodBetweenCallWaitingBursts>
        <disableLocalSpeedDialConfig>false</disableLocalSpeedDialConfig>
        <startMediaPort>13000</startMediaPort>
        <stopMediaPort>18000</stopMediaPort>
        <natEnabled>false</natEnabled>
        <natReceivedProcessing>false</natReceivedProcessing>
        <natAddress></natAddress>
        <sipLines>
            <!--        
    {{py:n = 1}}
    {{for extension in sip}}
    -->
            <line button="{{n}}" lineIndex="{{n}}">
                <featureID>9</featureID>
                <featureLabel>{{extension.extension}}</featureLabel>
                <proxy>USECALLMANAGER</proxy>
                <port>{{server_port}}</port>
                <name>{{extension.extension}}</name>
                <displayName>{{extension.extension}}</displayName>
                <autoAnswer>
                    <autoAnswerEnabled>0</autoAnswerEnabled>
                    <!-- "Auto Answer with Speakerphone" or "Auto Answer with Headset" -->
                    <autoAnswerMode>Auto Answer with Speakerphone</autoAnswerMode>
                </autoAnswer>
                <callWaiting>3</callWaiting>
                <authName>{{extension.account}}</authName>
                <authPassword>{{extension.secret}}</authPassword>
                <contact>{{extension.account}}</contact>
                <sharedLine>false</sharedLine>
                <messageWaitingLampPolicy>3</messageWaitingLampPolicy>
                <messageWaitingAMWI>0</messageWaitingAMWI>
                <messagesNumber>*97</messagesNumber>
                <ringSettingIdle>4</ringSettingIdle>
                <ringSettingActive>5</ringSettingActive>
                <forwardCallInfoDisplay>
                    <callerName>true</callerName>
                    <callerNumber>true</callerNumber>
                    <redirectedNumber>true</redirectedNumber>
                    <dialedNumber>true</dialedNumber>
                </forwardCallInfoDisplay>
                <maxNumCalls>{{max_sip_accounts}}</maxNumCalls>
                <busyTrigger>{{max_sip_accounts}}</busyTrigger>
                <recordingOption>enable</recordingOption>
            </line>
            <!--
    {{py:n += 1}}
    {{endfor}}
    -->
        </sipLines>
        <externalNumberMask></externalNumberMask>
        <voipControlPort>5060</voipControlPort>
        <dscpForAudio>184</dscpForAudio>
        <dscpVideo>136</dscpVideo>
        <ringSettingBusyStationPolicy>0</ringSettingBusyStationPolicy>
        <dialTemplate>DialTemplate.xml</dialTemplate>
        <softKeyFile></softKeyFile>
    </sipProfile>
    <MissedCallLoggingOption>1</MissedCallLoggingOption>
    <featurePolicyFile></featurePolicyFile>
    <commonProfile>
        <phonePassword></phonePassword>
        <backgroundImageAccess>true</backgroundImageAccess>
        <callLogBlfEnabled>0</callLogBlfEnabled>
    </commonProfile>
    <vendorConfig>
        <defaultWallpaperFile></defaultWallpaperFile>
        <disableSpeaker>false</disableSpeaker>
        <disableSpeakerAndHeadset>false</disableSpeakerAndHeadset>
        <enableMuteFeature>true</enableMuteFeature>
        <enableGroupListen>true</enableGroupListen>
        <holdResumeKey>0</holdResumeKey>
        <recentsSoftKey>1</recentsSoftKey>
        <dfBit>0</dfBit>
        <pcPort>0</pcPort> <!-- Disable the PC (computer) port. 0	Enabled	1	Disabled -->
        <spanToPCPort>1</spanToPCPort>
        <garp>0</garp>
        <rtcp>1</rtcp>
        <videoRtcp>1</videoRtcp>
        <voiceVlanAccess>1</voiceVlanAccess>
        <videoCapability>1</videoCapability>
        <hideVideoByDefault>0</hideVideoByDefault>
        <separateMute>0</separateMute>
        <ciscoCamera>1</ciscoCamera>
        <usb1>1</usb1>
        <usb2>1</usb2>
        <usbClasses>0,1,2</usbClasses>
        <sdio>1</sdio>
        <wifi>1</wifi>
        <bluetooth>1</bluetooth>
        <bluetoothProfile>0,1</bluetoothProfile>
        <btpbap>0</btpbap>
        <bthfu>0</bthfu>
        <ehookEnable>0</ehookEnable>
        <autoSelectLineEnable>1</autoSelectLineEnable>
        <autoCallSelect>1</autoCallSelect>
        <incomingCallToastTimer>5</incomingCallToastTimer>
        <dialToneFromReleaseKey>0</dialToneFromReleaseKey>
        <joinAndDirectTransferPolicy>0</joinAndDirectTransferPolicy>
        <minimumRingVolume></minimumRingVolume>
        <adminConfigurableRinger></adminConfigurableRinger>
        <simplifiedNewCall>0</simplifiedNewCall>
        <actionableAlert>0</actionableAlert>
        <showCallHistoryForSelectedLine>0</showCallHistoryForSelectedLine>
        <kemOneColumn>0</kemOneColumn>
        <lineMode>0</lineMode>
        <lowerYourVoiceAlert>0</lowerYourVoiceAlert>
        <markCallAsSpam>0</markCallAsSpam>
        <callParkMonitor>1</callParkMonitor>
        <allCallsOnPrimary>0</allCallsOnPrimary>
        <softKeyControl>1</softKeyControl>
        <settingsAccess>1</settingsAccess>
        <webProtocol>0</webProtocol>
        <webAccess>0</webAccess>  <!-- ! -->
        <webAdmin>1</webAdmin>
        <adminPassword>admin</adminPassword>
        <sshAccess>0</sshAccess>
        <detectCMConnectionFailure>0</detectCMConnectionFailure>
        <g722CodecSupport>1</g722CodecSupport>
        <handsetWidebandEnable>2</handsetWidebandEnable>
        <headsetWidebandEnable>2</headsetWidebandEnable>
        <headsetWidebandUIControl>1</headsetWidebandUIControl>
        <handsetWidebandUIControl>1</handsetWidebandUIControl>
        <daysDisplayNotActive>1,7</daysDisplayNotActive>
        <displayOnTime>08:00</displayOnTime>
        <displayOnDuration>10:00</displayOnDuration>
        <displayIdleTimeout>00:10</displayIdleTimeout>
        <displayOnWhenIncomingCall>1</displayOnWhenIncomingCall>
        <displayRefreshRate>0</displayRefreshRate>
        <daysBacklightNotActive>1,7</daysBacklightNotActive>
        <backlightOnTime>08:00</backlightOnTime>
        <backlightOnDuration>10:00</backlightOnDuration>
        <backlightIdleTimeout>00:10</backlightIdleTimeout>
        <backlightOnWhenIncomingCall>1</backlightOnWhenIncomingCall>
        <recordingTone>0</recordingTone>
        <recordingToneLocalVolume>100</recordingToneLocalVolume>
        <recordingToneRemoteVolume>50</recordingToneRemoteVolume>
        <recordingToneDuration></recordingToneDuration>
        <moreKeyReversionTimer>5</moreKeyReversionTimer>
        <peerFirmwareSharing>0</peerFirmwareSharing>
        <loadServer></loadServer>
        <problemReportUploadURL></problemReportUploadURL>
        <enableCdpSwPort>0</enableCdpSwPort>
        <enableCdpPcPort>0</enableCdpPcPort>
        <enableLldpSwPort>1</enableLldpSwPort>
        <enableLldpPcPort>0</enableLldpPcPort>
        <cdpEnable>0</cdpEnable>
        <powerNegotiation>0</powerNegotiation>
        <outOfRangeAlert>0</outOfRangeAlert>
        <scanningMode>2</scanningMode>
        <applicationURL></applicationURL>
        <appButtonTimer>0</appButtonTimer>
        <appButtonPriority>0</appButtonPriority>
        <specialNumbers></specialNumbers>
        <sendKeyAction>0</sendKeyAction>
        <powerOffWhenCharging>0</powerOffWhenCharging>
        <homeScreen>1</homeScreen>
        <accessContacts>1</accessContacts>
        <accessFavorites>1</accessFavorites>
        <accessVoicemail>1</accessVoicemail>
        <accessApps>1</accessApps>
    </vendorConfig>
    <versionStamp>d902ed5a-c1e5-4233-b1d6-a960d53d1c3a</versionStamp>
    <loadInformation></loadInformation>
    <inactiveLoadInformation></inactiveLoadInformation>
    <!-- <addOnModules>
    <addOnModule idx="1">
      <deviceType></deviceType>
      <deviceLine></deviceLine>
      <loadInformation></loadInformation>
    </addOnModule>
  </addOnModules> -->
    <!-- <phoneServices
    useHTTPS="false">
    <provisioning>2</provisioning>
    <phoneService type="1" category="0">
      <name>Missed Calls</name>
      <url>Application:Cisco/MissedCalls</url>
      <vendor></vendor>
      <version></version>
    </phoneService>
    <phoneService type="1" category="0">
      <name>Received Calls</name>
      <url>Application:Cisco/ReceivedCalls</url>
      <vendor></vendor>
      <version></version>
    </phoneService>
    <phoneService type="1" category="0">
      <name>Placed Calls</name>
      <url>Application:Cisco/PlacedCalls</url>
      <vendor></vendor>
      <version></version>
    </phoneService>
    <phoneService type="2" category="0">
      <name>Voicemail</name>
      <url>Application:Cisco/Voicemail</url>
      <vendor></vendor>
      <version></version>
    </phoneService> 
  </phoneServices> -->


    <!-- 
  <userLocale>
    <name>spanish_colombia</name>
    <uid>1</uid>
    <langCode>es_CO</langCode>
    <winCharSet>utf-8</winCharSet>
  </userLocale>
  <networkLocale>spanish_colombia</networkLocale>
  <networkLocaleInfo>
      <name>spanish_colombia</name>
      <uid>64</uid>
  </networkLocaleInfo>   -->
    <userLocale>
        <name></name>
        <uid>1</uid>
        <langCode></langCode>
        <version></version>
        <winCharSet>utf-8</winCharSet>
    </userLocale>
    <networkLocale></networkLocale>
    <networkLocaleInfo>
        <name></name>
        <version></version>
    </networkLocaleInfo>

    <idleTimeout>0</idleTimeout>
    <authenticationURL></authenticationURL>
    <messagesURL></messagesURL>
    <servicesURL></servicesURL>
    <directoryURL></directoryURL>
    <idleURL></idleURL>
    <informationURL></informationURL>
    <proxyServerURL></proxyServerURL>
    <secureAuthenticationURL></secureAuthenticationURL>
    <secureMessagesURL></secureMessagesURL>
    <secureServicesURL></secureServicesURL>
    <secureDirectoryURL></secureDirectoryURL>
    <secureInformationURL></secureInformationURL>
    <secureIdleURL></secureIdleURL>
    <!-- What protocol the phone will use to connect to Asterisk. 
  Only use 1 (TCP) or 3 (TLS), as the phone causes SIP retransmit errors when using UDP.
  Note: <deviceSecurityMode> must be set to either 2 (Authenticated) 
  or 3 (Encrypted) to enable TLS as well as configuring Device Security.
      1 	TCP 	2 	UDP 	3 	TLS -->
    <transportLayerProtocol>2</transportLayerProtocol>
    <!-- 1 	Insecure 	2 	Authenticated (TLS using NULL cipher) 	3 	Encrypted (TLS using AES cipher) -->
    <deviceSecurityMode>1</deviceSecurityMode>
    <TLSResumptionTimer>3600</TLSResumptionTimer>
    <phonePersonalization>1</phonePersonalization>
    <autoCallPickupEnable>true</autoCallPickupEnable>
    <blfAudibleAlertSettingOfIdleStation>0</blfAudibleAlertSettingOfIdleStation>
    <blfAudibleAlertSettingOfBusyStation>0</blfAudibleAlertSettingOfBusyStation>
    <dndCallAlert>1</dndCallAlert>
    <dndReminderTimer>5</dndReminderTimer>
    <advertiseG722Codec>1</advertiseG722Codec>
    <rollover>0</rollover>
    <joinAcrossLines>0</joinAcrossLines>
    <capfAuthMode>0</capfAuthMode>
    <!-- <capfList>
    <capf>
      <phonePort>3804</phonePort>
      <processNodeName></processNodeName>
    </capf>
  </capfList> -->
    <certHash></certHash>
    <encrConfig>false</encrConfig>
    <userId></userId>
    <ownerId></ownerId>
    <sshUserId></sshUserId>
    <sshPassword></sshPassword>
</device>