
if {[namespace exists TestCenter] == 1} {
	namespace delete TestCenter
}

namespace eval TestCenter {

	variable resultDataSet_Array
	variable statViews_Array
	
	variable project ""
	
	::struct::record define statView_Record {resultType configTypes group description}
}

proc ::TestCenter::SetStatsViews {curProject} {

	variable resultDataSet_Array
	variable statViews_Array
	variable project
	
	set project $curProject

	foreach instance [::struct::record show instance ::TestCenter::statView_Record] {
		::struct::record delete instance $instance
	}

	array unset resultDataSet_Array
	array unset statViews_Array

	set i 0
	array set statViews_Array "

        analyzerportresults			            [statView_Record sv_R[incr i]	-resultType AnalyzerPortResults			            -configTypes Analyzer					-group Port			        -description "Port RX counters"]
        ancpaccessnoderesults			        [statView_Record sv_R[incr i]	-resultType AncpAccessNodeResults			        -configTypes AncpAccessNodeConfig		-group Access               -description "ANCP Access Node counters"]
        ancpportresults			                [statView_Record sv_R[incr i]	-resultType AncpPortResults			                -configTypes AncpPortConfig		        -group Access               -description "ANCP Port counters"]
    	arpndresults 				            [statView_Record sv_R[incr i]	-resultType ArpNdResults				            -configTypes Port						-group Port			        -description "ARP Port counters"]
        bfdipv4sessionresults 			        [statView_Record sv_R[incr i]	-resultType BfdIpv4SessionResults			        -configTypes BfdRouterConfig			-group Routing_and_MPLS     -description "BFD IPv4 Session counters"]
        bfdipv6sessionresults 			        [statView_Record sv_R[incr i]	-resultType BfdIpv6SessionResults			        -configTypes BfdRouterConfig			-group Routing_and_MPLS     -description "BFD IPv6 Session counters"]
        bfdrouterresults 			            [statView_Record sv_R[incr i]	-resultType BfdRouterResults			            -configTypes BfdRouterConfig			-group Routing_and_MPLS     -description "BFD Router counters"]
        bfdsessionresults 			            [statView_Record sv_R[incr i]	-resultType BfdSessionResults			            -configTypes BfdRouterConfig			-group Routing_and_MPLS     -description "BFD Session counters"]
        bgprouterresults 			            [statView_Record sv_R[incr i]	-resultType BgpRouterResults			            -configTypes BgpRouterConfig			-group Routing_and_MPLS     -description "BGP Router counters"]
        cifsclientresults 			            [statView_Record sv_R[incr i]	-resultType CifsClientResults			            -configTypes CifsClientProtocolConfig	-group Applications         -description "CIFS Client results"]
        cifsserverresults 			            [statView_Record sv_R[incr i]	-resultType CifsServerResults			            -configTypes CifsServerProtocolConfig	-group Applications         -description "CIFS Server results"]
        dhcpv4blockresults			            [statView_Record sv_R[incr i]	-resultType Dhcpv4BlockResults			            -configTypes Dhcpv4BlockConfig			-group Access	            -description ""]
        dhcpv4portresults			            [statView_Record sv_R[incr i]	-resultType Dhcpv4PortResults			            -configTypes Dhcpv4PortConfig			-group Access	            -description ""]
        dhcpv4serverresults		                [statView_Record sv_R[incr i]	-resultType Dhcpv4ServerResults		                -configTypes Dhcpv4ServerConfig			-group Access	            -description "DHCPv4 server results"]
        dhcpv4sessionresults		            [statView_Record sv_R[incr i]	-resultType Dhcpv4SessionResults		            -configTypes Dhcpv4BlockConfig			-group Access	            -description ""]
    	dhcpv6portresults			            [statView_Record sv_R[incr i]	-resultType Dhcpv6PortResults			            -configTypes Dhcpv6PortConfig			-group Access	            -description ""]
        diffservresults				            [statView_Record sv_R[incr i]	-resultType DiffServResults				            -configTypes Analyzer					-group Port			        -description ""]
    	eoamaisresults				            [statView_Record sv_R[incr i]	-resultType EoamAisResults				            -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamcontchklocalresults		            [statView_Record sv_R[incr i]	-resultType EoamContChkLocalResults				    -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamcontchkremoteresults	            [statView_Record sv_R[incr i]	-resultType EoamContChkRemoteResults				-configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamdelaymeasurementmessagerxresults	[statView_Record sv_R[incr i]	-resultType EoamDelayMeasurementMessageRxResults	-configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamdelaymeasurementresponserxresults	[statView_Record sv_R[incr i]	-resultType EoamDelayMeasurementResponseRxResults   -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamdelaymeasurementresults	            [statView_Record sv_R[incr i]	-resultType EoamDelayMeasurementResults             -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlckresults	                        [statView_Record sv_R[incr i]	-resultType EoamLckResults                          -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlinktracemessagerxresults	        [statView_Record sv_R[incr i]	-resultType EoamLinkTraceMessageRxResults           -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlinktracemessagetxresults	        [statView_Record sv_R[incr i]	-resultType EoamLinkTraceMessageTxResults           -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlinktracepathresults	            [statView_Record sv_R[incr i]	-resultType EoamLinkTracePathResults                -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlinktraceresponserxresults	        [statView_Record sv_R[incr i]	-resultType EoamLinkTraceResponseRxResults          -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlinktraceresponsetxresults	        [statView_Record sv_R[incr i]	-resultType EoamLinkTraceResponseTxResults          -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlinktraceresults	                [statView_Record sv_R[incr i]	-resultType EoamLinkTraceResults                    -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamloopbackmessagerxresults	        [statView_Record sv_R[incr i]	-resultType EoamLoopbackMessageRxResults            -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamloopbackmessagetxresults	        [statView_Record sv_R[incr i]	-resultType EoamLoopbackMessageTxResults            -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamloopbackresponserxresults	        [statView_Record sv_R[incr i]	-resultType EoamLoopbackResponseRxResults           -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamloopbackresponsetxresults	        [statView_Record sv_R[incr i]	-resultType EoamLoopbackResponseTxResults           -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamloopbackresults	                    [statView_Record sv_R[incr i]	-resultType EoamLoopbackResults                     -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlossmeasurementmessagerxresults     [statView_Record sv_R[incr i]	-resultType EoamLossMeasurementMessageRxResults     -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlossmeasurementresponserxresults	[statView_Record sv_R[incr i]	-resultType EoamLossMeasurementResponseRxResults    -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoamlossmeasurementresults	            [statView_Record sv_R[incr i]	-resultType EoamLossMeasurementResponseRxResults    -configTypes EoamMaintenancePointConfig	-group Carrier_Ethernet	    -description ""]
    	eoammegresults	                        [statView_Record sv_R[incr i]	-resultType EoamMegResults                          -configTypes EoamMegConfig              -group Carrier_Ethernet	    -description ""]
    	eoamportresults	                        [statView_Record sv_R[incr i]	-resultType EoamPortResults                         -configTypes EoamPortConfig             -group Carrier_Ethernet	    -description ""]
        filteredstreamresults		            [statView_Record sv_R[incr i]	-resultType FilteredStreamResults		            -configTypes Analyzer					-group Streams	            -description ""]
    	generatorportresults		            [statView_Record sv_R[incr i]	-resultType GeneratorPortResults		            -configTypes Generator					-group Port			        -description "Port TX counters"]
    	igmpgroupmembershipresults	            [statView_Record sv_R[incr i]	-resultType IgmpGroupMembershipResults	            -configTypes IgmpGroupMembership		-group Multicast			-description ""]
    	igmphostresults				            [statView_Record sv_R[incr i]	-resultType IgmpHostResults				            -configTypes IgmpHostConfig				-group Multicast			-description ""]
    	igmpportresults				            [statView_Record sv_R[incr i]	-resultType IgmpPortResults				            -configTypes IgmpPortConfig				-group Multicast			-description ""]
    	igmprouterresults			            [statView_Record sv_R[incr i]	-resultType IgmpRouterResults			            -configTypes IgmpRouterConfig			-group Multicast			-description ""]
    	iptvportresults				            [statView_Record sv_R[incr i]	-resultType IptvPortResults				            -configTypes Port						-group Triple_Play			-description ""]
    	iptvchannelresults			            [statView_Record sv_R[incr i]	-resultType IptvChannelResults			            -configTypes IptvViewedChannels			-group Triple_Play			-description ""]
    	iptvstbblockresults			            [statView_Record sv_R[incr i]	-resultType IptvStbBlockResults			            -configTypes IptvStbBlockConfig			-group Triple_Play			-description ""]
    	iptvviewingprofileresults	            [statView_Record sv_R[incr i]	-resultType IptvViewingProfileResults	            -configTypes IptvViewingProfileConfig	-group Triple_Play			-description ""]
    	iptvtestresults				            [statView_Record sv_R[incr i]	-resultType IptvTestResults				            -configTypes Project					-group Triple_Play			-description ""]
    	isisrouterresults			            [statView_Record sv_R[incr i]	-resultType IsisRouterResults			            -configTypes IsisRouterConfig			-group Routing_and_MPLS		-description ""]
    	lacpportresults				            [statView_Record sv_R[incr i]	-resultType LacpPortConfig				            -configTypes IsisRouterConfig			-group Switching			-description ""]
    	ldplspresults				            [statView_Record sv_R[incr i]	-resultType LdpLspResults				            -configTypes LdpRouterConfig			-group Routing_and_MPLS		-description ""]
    	ldprouterresults			            [statView_Record sv_R[incr i]	-resultType LdpRouterResults			            -configTypes LdpRouterConfig			-group Routing_and_MPLS		-description ""]
    	mldgroupmembershipresults	            [statView_Record sv_R[incr i]	-resultType MldGroupMembershipResults	            -configTypes MldGroupMembership			-group Multicast			-description ""]
    	mldhostresults				            [statView_Record sv_R[incr i]	-resultType MldHostResults				            -configTypes MldHostConfig				-group Multicast			-description ""]
    	mldportresults				            [statView_Record sv_R[incr i]	-resultType MldPortResults				            -configTypes MldPortConfig				-group Multicast			-description ""]
    	mldrouterresults			            [statView_Record sv_R[incr i]	-resultType MldRouterResults			            -configTypes MldRouterConfig			-group Multicast			-description ""]
    	ospfv2routerresults			            [statView_Record sv_R[incr i]	-resultType Ospfv2RouterResults			            -configTypes Ospfv2RouterConfig			-group Routing_and_MPLS		-description ""]
    	ospfv3routerresults			            [statView_Record sv_R[incr i]	-resultType Ospfv3RouterResults			            -configTypes Ospfv3RouterConfig			-group Routing_and_MPLS		-description ""]
    	overflowresults				            [statView_Record sv_R[incr i]	-resultType OverflowResults				            -configTypes Analyzer					-group Port			        -description ""]
    	pimrouterresults			            [statView_Record sv_R[incr i]	-resultType PimRouterResults			            -configTypes PimRouterConfig			-group Routing_and_MPLS		-description ""]
    	portavglatencyresults		            [statView_Record sv_R[incr i]	-resultType PortAvgLatencyResults		            -configTypes Analyzer					-group Port			        -description ""]
    	pppprotocolresults			            [statView_Record sv_R[incr i]	-resultType PppProtocolResults			            -configTypes PppProtocolConfig			-group Access			    -description ""]
    	riprouterresults			            [statView_Record sv_R[incr i]	-resultType RipRouterResults			            -configTypes RipRouterConfig			-group Routing_and_MPLS		-description ""]
    	rsvplspresults				            [statView_Record sv_R[incr i]	-resultType RsvpLspResults				            -configTypes RsvpRouterConfig			-group Routing_and_MPLS		-description ""]
    	rsvprouterresults			            [statView_Record sv_R[incr i]	-resultType RsvpRouterResults			            -configTypes RsvpRouterConfig			-group Routing_and_MPLS		-description ""]
    	sonetresults				            [statView_Record sv_R[incr i]	-resultType SonetResults				            -configTypes Port						-group Port			        -description ""]
    	sonetalarmsresults			            [statView_Record sv_R[incr i]	-resultType SonetAlarmsResults			            -configTypes Port						-group Port			        -description ""]
    	rxcpuportresults			            [statView_Record sv_R[incr i]	-resultType RxCpuPortResults			            -configTypes Analyzer					-group Port			        -description ""]
    	rxportpairresults			            [statView_Record sv_R[incr i]	-resultType RxPortPairResults			            -configTypes Port						-group Port			        -description ""]
    	rxstreamblockresults		            [statView_Record sv_R[incr i]	-resultType RxStreamBlockResults		            -configTypes StreamBlock				-group Streams	            -description ""]
    	rxstreamresults				            [statView_Record sv_R[incr i]	-resultType RxStreamResults				            -configTypes StreamBlock				-group Streams	            -description ""]
    	rxstreamsummaryresults		            [statView_Record sv_R[incr i]	-resultType RxStreamSummaryResults		            -configTypes StreamBlock				-group Streams	            -description ""]
    	txcpuportresults			            [statView_Record sv_R[incr i]	-resultType TxCpuPortResults			            -configTypes Generator					-group Port			        -description ""]
    	txportpairresults			            [statView_Record sv_R[incr i]	-resultType TxPortPairResults			            -configTypes Port						-group Port			        -description ""]
    	txstreamblockresults		            [statView_Record sv_R[incr i]	-resultType TxStreamBlockResults		            -configTypes StreamBlock				-group Streams	            -description ""]
    	txstreamresults				            [statView_Record sv_R[incr i]	-resultType TxStreamResults				            -configTypes StreamBlock				-group Streams	            -description ""]

        bridgeportresults       [statView_Record sv_R[incr i]	-resultType BridgePortResults			-configTypes {BridgePortConfig MstiConfig}						                                                                                                                                        -group Switching	-description "STP/MSTP counters"]
    	dhcpv6blockresults		[statView_Record sv_R[incr i]	-resultType Dhcpv6BlockResults			-configTypes {Dhcpv6PdBlockConfig Dhcpv6BlockConfig} 																																					-group Access	    -description ""]
    	dhcpv6sessionresults	[statView_Record sv_R[incr i]	-resultType Dhcpv6SessionResults		-configTypes {Dhcpv6PdBlockConfig Dhcpv6BlockConfig} 																																					-group Access	    -description ""]
    	pppoeportresults		[statView_Record sv_R[incr i]	-resultType PppoePortResults			-configTypes {PppoaClientBlockConfig PppoaServerBlockConfig PppoeClientBlockConfig PppoeServerBlockConfig PppoL2tpv2ClientBlockConfig PppoL2tpv2ServerBlockConfig PppoxPortConfig PppProtocolConfig}	-group Access	    -description ""]
    	pppoesessionresults	    [statView_Record sv_R[incr i]	-resultType PppoeSessionResults			-configTypes {PppoeClientBlockConfig PppoeServerBlockConfig}																																			-group Access	    -description ""]
    	rxtrafficgroupresults	[statView_Record sv_R[incr i]	-resultType RxTrafficGroupResults		-configTypes {StreamBlock TrafficGroup}																																									-group Streams      -description ""]
    	txtrafficgroupresults   [statView_Record sv_R[incr i]	-resultType TxTrafficGroupResults		-configTypes {StreamBlock TrafficGroup}																																									-group Streams      -description ""]

    "

}


proc ::TestCenter::Subscribe {view {configTypes {}} {resultParent {}} {resultsFile {}} {interval 1}} {
	variable statViews_Array
	variable resultDataSet_Array
	variable project
		
	set viewL [string tolower $view]		
	if {$configTypes == ""} {
		if {[array names statViews_Array $viewL] == ""} {
			error "TSTclError - Invalid Statistics View $view"
		}
		set configTypes [$statViews_Array($viewL) cget -configTypes]
	}
	if {$resultParent == {}} {
		set resultParent $project
	}
	set actualResultsFile {}
	if {$resultsFile != ""} {
		set actualResultsFile [SetResultsSetting $resultsFile]
		set resultsFile [file tail $resultsFile]
	}
	# Note that if configTypes = "" but resultsFile != "" then all configuration types will subscribe to the same file.
	# In this case all results will be written to the same file.
	foreach configType $configTypes {
		set resultDataSet_Array($viewL,$configType) [stc::subscribe -parent $project -resultParent $resultParent -configType $configType -resultType $view -RecordsPerPage 256 -FileNamePrefix $resultsFile -Interval $interval]
	}
	return $actualResultsFile
}

# Unsubscribe view from ALL available config types
proc ::TestCenter::Unsubscribe {view} {
	variable resultDataSet_Array
	set viewL [string tolower $view]		
	foreach resultDataSet [array names resultDataSet_Array $viewL*] {
		stc::unsubscribe $resultDataSet_Array($resultDataSet)
	}
	array unset resultDataSet_Array $viewL*
}
	
proc ::TestCenter::GetViews {} {
	variable statViews_Array
	set statViews {}
	foreach statView [array names statViews_Array] {			
		lappend statViews [$statViews_Array($statView) cget -group]\t[$statViews_Array($statView) cget -resultType]\t[$statViews_Array($statView) cget -configTypes]\t[$statViews_Array($statView) cget -description]\n
	}
	return List\n[join $statViews ""]
}

proc ::TestCenter::GetStatistics {view {results {}} {configType {}}} {
	variable statViews_Array
	variable resultDataSet_Array
	variable project		

	set viewL [string tolower $view]		
	if {$configType == ""} {
		set configType [$statViews_Array($viewL) cget -configTypes] 
	}
	if {[array names resultDataSet_Array $viewL,$configType] == ""} {
		error "TSTclError - Statistics view $view,$configType not subscribed"
	}
	stc::perform RefreshResultView -ResultDataSet $resultDataSet_Array($viewL,$configType)
		
	if {$configType == "User"} {
		return [GetUserStatistics $view]
	}
		
	array set allResultsA {}
	set totalPageCount [stc::get $resultDataSet_Array($viewL,$configType) -TotalPageCount]
	for {set pageNumber 1} {$pageNumber <= $totalPageCount} {incr pageNumber} {
		stc::config $resultDataSet_Array($viewL,$configType) -PageNumber $pageNumber
		foreach resultHandle [stc::get $resultDataSet_Array($viewL,$configType) -ResultHandleList] {
			array set resultsA [stc::get $resultHandle]
			set parent $resultsA(-parent)
			set parents $parent
			# Note that for results with parent == Project the name will be empty (in 4.00 the only known case is IptvTestResults)
			set name ""
			while {$parent != $project} {
				if {$name == "" && ([regexp ^port $parent] == 1 || [regexp ^emulateddevice $parent] == 1 || [regexp ^streamblock $parent] == 1)} {
					set name [stc::get $parent -name]					
				}
				set parent [stc::get $parent -parent]
				set parents $parent/$parents
			}
			append allResultsA(object) $resultHandle \t
			append allResultsA(parents) $parents \t
			append allResultsA(topLevelName) $name \t	
			array unset resultsA -parent
			array unset resultsA -Name
			array unset resultsA -resultchild-Sources
			foreach result [array names resultsA] {
				if {$results == {} || [lsearch -nocase $results [string range $result 1 end]] >= 0} { 
					append allResultsA([string range $result 1 end]) $resultsA($result) \t
				}
			}
		}
	}
	
	return [string trim [::TrafficGenerator::array2list allResultsA]]\nListDelimiter\nSystem

}
	
proc ::TestCenter::GetUserStatistics {view} {
	variable statViews_Array
	variable resultDataSet_Array
	variable requiredDrillDownStats

	set requiredStats ListDelimiter\n

	set viewL [string tolower $view]		
	if {[regexp {dynamic*} $resultDataSet_Array($viewL,User)]} {
		stc::perform UpdateDynamicResultViewCommand -DynamicResultView $resultDataSet_Array($viewL,User)
		after 2000
		set presentationResultQuery [stc::get $resultDataSet_Array($viewL,User) -children-PresentationResultQuery]
		set selectProperties [stc::get $presentationResultQuery -SelectProperties]
		append requiredStats [join $selectProperties \t]\n
		foreach resultViewData [stc::get $presentationResultQuery -children-ResultViewData]  {
			set requiredDrillDownStats {}
			append requiredStats [::TestCenter::GetDynamicStatistics $resultViewData [llength $selectProperties]]\n
		}
		return ${requiredStats}ListDelimiter\nDynamic
	}
	foreach resultquery [stc::get $resultDataSet_Array($viewL,User) -children-resultquery] {
		set resultClassId [stc::get $resultquery -ResultClassId]
		if {$resultClassId == {}} {
			continue
		}
		set allStats [::TestCenter::GetStatistics $resultClassId]
		set allStatsList [lrange [split [string range $allStats [string length ListDelimiter] end] \n] 1 end]
		foreach propertyId [stc::get $resultquery -PropertyIdArray] {
			set propertyId [string map {multicastportresults igmpportresults} $propertyId]	
			set requiredStat [string map "$resultClassId. {}" $propertyId]
			set found false
			foreach stat $allStatsList {
				if {[lsearch -glob [string tolower $stat]* -$requiredStat] == 0} {
					append requiredStats [string map "[lindex $stat 0] [lindex $stat 0]\\t$resultClassId" $stat] \n  
					set found true
					continue
				}
			}
			if {!$found} {
				error "TSTclError - Statistics $propertyId does not exist, check the user view definitions / subscriptions"		
			}
		}
	}
	append requiredStats [string map "topLevelName topLevelName\\t" [lsearch -inline -index 0 $allStatsList topLevelName]] \n 		
	return ${requiredStats}ListDelimiter\nUser
}
		
proc ::TestCenter::GetDynamicStatistics {resultViewData numColumns} {
	variable requiredDrillDownStats

	if {[string length $resultViewData] != 0} {
		append requiredDrillDownStats [join [lrange [stc::get $resultViewData -ResultData] 0 [expr $numColumns - 1]] \t]\n
		stc::perform ExpandResultViewDataCommand -ResultViewData $resultViewData
		foreach childrvd [stc::get $resultViewData -children-ResultViewData] {
			::TestCenter::GetDynamicStatistics $childrvd $numColumns
		}
	}
	return [string trim $requiredDrillDownStats]

}
	
# Does not support paging
proc ::TestCenter::SaveStatistics {resultsFile view {configType {}}} {
	variable statViews_Array
	variable resultDataSet_Array
	variable project
		
	set viewL [string tolower $view]				
	if {$configType == ""} {
		set configType [$statViews_Array($viewL) cget -configTypes] 
	}
	if {[array names resultDataSet_Array $viewL,$configType] == ""} {
		error "TSTclError - Statistics view $view,$configType not subscribed"
	}
	set actualResultsFile [SetResultsSetting $resultsFile]
	stc::perform ExportResults -Filenameprefix [file tail $resultsFile] -ResultView $resultDataSet_Array($viewL,$configType)
	return $actualResultsFile
}
	
proc ::TestCenter::SetResultsSetting {resultsFile} {
	variable project
	set resultSetting [stc::get $project -children-TestResultSetting]
	stc::config $resultSetting -ResultsDirectory [file dirname $resultsFile] -SaveResultsRelativeTo None
	array set paths [stc::perform GetTestResultSettingPaths]
	return [file join $paths(-OutputBasePath) [file tail $resultsFile]].csv
}

proc ::TestCenter::XableLsas {router xable} {
	set lsas [stc::get $router -children-ExternalLsaBlock]
	lappend lsas {*}[stc::get $router -children-AsbrSummaryLsa]
	lappend lsas {*}[stc::get $router -children-SummaryLsaBlock]
	lappend lsas {*}[stc::get $router -children-NetworkLsa]
	lappend lsas {*}[stc::get $router -children-RouterLsa]
		for {set firstLsa 0} {[expr $firstLsa + 64] < [llength $lsas]} {set firstLsa [expr $firstLsa + 64]} {
		set lastLsa [expr $firstLsa + 63]
		foreach lsa [lrange $lsas $firstLsa $lastLsa] {
			if {[stc::get $lsa -name] != "Default Router"} {
				stc::config $lsa -Active $xable
			}
		}
		stc::apply
		after 512
	}
	foreach lsa [lrange $lsas [incr lastLsa] [llength $lsas]] {
		if {[stc::get $lsa -name] != "Default Router"} {
			stc::config $lsa -Active $xable
		}
	}
	stc::apply
	after 512
}
