function GetOciTopLevelCommand_psa() {
    return 'psa'
}

function GetOciSubcommands_psa() {
    $ociSubcommands = @{
        'psa' = 'private-service-access psa-services work-request work-request-error work-request-log'
        'psa private-service-access' = 'change-compartment create delete get list update'
        'psa psa-services' = 'list'
        'psa work-request' = 'cancel get list'
        'psa work-request-error' = 'list'
        'psa work-request-log' = 'list'
    }
    return $ociSubcommands
}

function GetOciCommandsToLongParams_psa() {
    $ociCommandsToLongParams = @{
        'psa private-service-access change-compartment' = 'compartment-id from-json help if-match max-wait-seconds private-service-access-id wait-for-state wait-interval-seconds'
        'psa private-service-access create' = 'compartment-id defined-tags description display-name freeform-tags from-json help ipv4-ip max-wait-seconds nsg-ids security-attributes service-id subnet-id wait-for-state wait-interval-seconds'
        'psa private-service-access delete' = 'force from-json help if-match max-wait-seconds private-service-access-id wait-for-state wait-interval-seconds'
        'psa private-service-access get' = 'from-json help private-service-access-id'
        'psa private-service-access list' = 'all compartment-id display-name from-json help id lifecycle-state limit page page-size service-id sort-by sort-order vcn-id'
        'psa private-service-access update' = 'defined-tags description display-name force freeform-tags from-json help if-match max-wait-seconds nsg-ids private-service-access-id security-attributes wait-for-state wait-interval-seconds'
        'psa psa-services list' = 'all display-name from-json help limit page page-size service-id sort-by sort-order'
        'psa work-request cancel' = 'force from-json help if-match work-request-id'
        'psa work-request get' = 'from-json help work-request-id'
        'psa work-request list' = 'all compartment-id from-json help limit page page-size resource-id sort-by sort-order status work-request-id'
        'psa work-request-error list' = 'all from-json help limit page page-size sort-by sort-order work-request-id'
        'psa work-request-log list' = 'all from-json help limit page page-size sort-by sort-order work-request-id'
    }
    return $ociCommandsToLongParams
}

function GetOciCommandsToShortParams_psa() {
    $ociCommandsToShortParams = @{
        'psa private-service-access change-compartment' = '? c h'
        'psa private-service-access create' = '? c h'
        'psa private-service-access delete' = '? h'
        'psa private-service-access get' = '? h'
        'psa private-service-access list' = '? c h'
        'psa private-service-access update' = '? h'
        'psa psa-services list' = '? h'
        'psa work-request cancel' = '? h'
        'psa work-request get' = '? h'
        'psa work-request list' = '? c h'
        'psa work-request-error list' = '? h'
        'psa work-request-log list' = '? h'
    }
    return $ociCommandsToShortParams
}