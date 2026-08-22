$readed = @{
    "database_k" = @{
        "table_schema" = @{
            "table_name" = @{"read_time" = @("readed_paths")

            }
        }
    }
}

($readed | ConvertTo-Json -Depth 20) > $PSScriptRoot\.readed.json

