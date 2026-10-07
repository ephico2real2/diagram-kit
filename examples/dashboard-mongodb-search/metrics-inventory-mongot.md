# Metrics inventory

Source: `{namespace="mongodb-poc",job="mongot-search-0-svc"}`

1024 metric names in 828 families, 5489 series.

| Declared type | Families |
| --- | --- |
| counter | 209 |
| gauge | 465 |
| histogram | 5 |
| summary | 141 |
| unknown | 8 |

726 of the 1024 names did not change on any series in the last 1h.

## mongot_HealthCheckServer (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_HealthCheckServer_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_HealthCheckServer_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_HealthCheckServer_executor_idle_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_HealthCheckServer_executor_idle_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_HealthCheckServer_executor_idle_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_HealthCheckServer_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_HealthCheckServer_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_HealthCheckServer_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_HealthCheckServer_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_HealthCheckServer_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_HealthCheckServer_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_HealthCheckServer_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_HealthCheckServer_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_HealthCheckServer_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_HealthCheckServer_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_auto (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_auto_embedding_session_refresh_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_auto_embedding_session_refresh_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_auto_embedding_session_refresh_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_auto_embedding_session_refresh_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_auto_embedding_session_refresh_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_auto_embedding_session_refresh_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_auto_embedding_session_refresh_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_auto_embedding_session_refresh_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_auto_embedding_session_refresh_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_auto_embedding_session_refresh_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_auto_embedding_session_refresh_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_auto_embedding_session_refresh_executor_scheduled_repetitively_total` | counter | 3 | 0 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_auto_embedding_session_refresh_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_auto_embedding_session_refresh_executor_seconds_max` | gauge | 3 | 3 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_auto_embedding_session_refresh_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_autoEmbedding (47)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_scheduled_repetitively_total` | counter | 3 | 0 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_autoEmbedding_change_stream_mode_selector_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_change_stream_sync_dispatcher_executor_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_decoding_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_autoEmbedding_decoding_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_decoding_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_decoding_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_decoding_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_decoding_executor_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_autoEmbedding_mongoClient_connectionPool_connections` | gauge | 6 | 0 | 1 | Scope (1), clientName (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_mongoClient_connectionPool_connectionsCheckedOut` | gauge | 6 | 0 | 1 | Scope (1), clientName (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_autoEmbedding_mongoClient_connectionPool_maxSize` | gauge | 6 | 0 | 2 | Scope (1), clientName (2) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_autoEmbedding_mongoClient_connectionPool_minSize` | gauge | 6 | 0 | 1 | Scope (1), clientName (2) | constant, the same on every series: a number or a table row, not a line |

## mongot_blobstore (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_blobstore_lifecycle_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_blobstore_lifecycle_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_blobstore_lifecycle_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_idle_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_blobstore_lifecycle_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_blobstore_lifecycle_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blobstore_lifecycle_executor_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_blocking (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_blocking_server_worker_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blocking_server_worker_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_blocking_server_worker_executor_idle_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_blocking_server_worker_executor_idle_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_blocking_server_worker_executor_idle_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_blocking_server_worker_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blocking_server_worker_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blocking_server_worker_executor_pool_size_threads` | gauge | 3 | 3 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_blocking_server_worker_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blocking_server_worker_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_blocking_server_worker_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_blocking_server_worker_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_blocking_server_worker_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_change (30)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_change_stream_mode_selector_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_mode_selector_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_change_stream_mode_selector_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_change_stream_mode_selector_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_mode_selector_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_change_stream_mode_selector_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_mode_selector_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_mode_selector_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_mode_selector_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_mode_selector_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_mode_selector_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_change_stream_mode_selector_executor_scheduled_repetitively_total` | counter | 3 | 0 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_change_stream_mode_selector_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_change_stream_mode_selector_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_change_stream_mode_selector_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_change_stream_sync_dispatcher_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_sync_dispatcher_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_change_stream_sync_dispatcher_executor_idle_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_change_stream_sync_dispatcher_executor_idle_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_change_stream_sync_dispatcher_executor_idle_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_change_stream_sync_dispatcher_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_sync_dispatcher_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_sync_dispatcher_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_sync_dispatcher_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_sync_dispatcher_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_change_stream_sync_dispatcher_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_change_stream_sync_dispatcher_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_change_stream_sync_dispatcher_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_change_stream_sync_dispatcher_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_change_stream_sync_dispatcher_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_changestream (2)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_changestream_numFragmentOpTimeMismatches_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_changestream_numSplitEvents_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |

## mongot_command (68)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_command_buildinfoCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_buildinfoCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_buildinfoCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_buildinfoCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_getMoreCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_getMoreCommandSerializationLatency_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_getMoreCommandSerializationLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_getMoreCommandSerializationLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_getMoreCommandSerializationLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_getMoreCommandTotalLatency_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_getMoreCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_getMoreCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_getMoreCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_helloCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_helloCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_helloCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_helloCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_isMasterCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_isMasterCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_isMasterCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_isMasterCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_ismasterCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_ismasterCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_ismasterCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_ismasterCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_killCursorsCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_killCursorsCommandTotalLatency_seconds_count` | summary | 3 | 1 | 2 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_killCursorsCommandTotalLatency_seconds_max` | gauge | 3 | 1 | 1 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_command_killCursorsCommandTotalLatency_seconds_sum` | summary | 3 | 1 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_manageSearchIndexCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_manageSearchIndexCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_manageSearchIndexCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_manageSearchIndexCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_pingCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_pingCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_pingCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_pingCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_planShardedSearchCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_planShardedSearchCommandSerializationLatency_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_planShardedSearchCommandSerializationLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_planShardedSearchCommandSerializationLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_planShardedSearchCommandSerializationLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_planShardedSearchCommandTotalLatency_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_planShardedSearchCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_planShardedSearchCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_planShardedSearchCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchBetaCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_searchBetaCommandTotalLatency_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchBetaCommandTotalLatency_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_command_searchBetaCommandTotalLatency_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_searchCommandSerializationLatency_seconds` | summary | 12 | 12 | 10 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchCommandSerializationLatency_seconds_count` | summary | 3 | 3 | 2 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchCommandSerializationLatency_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_command_searchCommandSerializationLatency_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchCommandTotalLatency_seconds` | summary | 12 | 12 | 10 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchCommandTotalLatency_seconds_count` | summary | 3 | 3 | 2 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_searchCommandTotalLatency_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_command_searchCommandTotalLatency_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_vectorSearchCommandFailure_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_command_vectorSearchCommandSerializationLatency_seconds` | summary | 12 | 12 | 7 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_vectorSearchCommandSerializationLatency_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_vectorSearchCommandSerializationLatency_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_command_vectorSearchCommandSerializationLatency_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_vectorSearchCommandTotalLatency_seconds` | summary | 12 | 12 | 6 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_vectorSearchCommandTotalLatency_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_command_vectorSearchCommandTotalLatency_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_command_vectorSearchCommandTotalLatency_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_concurrent (26)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_concurrent_search_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_concurrent_search_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_concurrent_search_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_concurrent_search_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_concurrent_search_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_search_executor_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_concurrent_vector_rescoring_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_concurrent_vector_rescoring_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_concurrent_vector_rescoring_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_concurrent_vector_rescoring_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_concurrent_vector_rescoring_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_concurrent_vector_rescoring_executor_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_config (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_config_monitor_executor_active_threads` | gauge | 3 | 2 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_config_monitor_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_config_monitor_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_config_monitor_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_config_monitor_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_config_monitor_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_config_monitor_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_config_monitor_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_config_monitor_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_config_monitor_executor_queued_tasks` | gauge | 3 | 2 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_config_monitor_executor_scheduled_once_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_config_monitor_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_config_monitor_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_config_monitor_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_config_monitor_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_configState (7)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_configState_indexesInCatalog` | gauge | 6 | 0 | 2 | Scope (1), indexFormatVersion (2) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_configState_indexesInCatalogFeatureVersionFour` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_configState_indexesPhasingOut` | gauge | 6 | 0 | 1 | Scope (1), indexFormatVersion (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_configState_indexesPhasingOutFeatureVersionFour` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_configState_stagedIndexes` | gauge | 6 | 0 | 1 | Scope (1), indexFormatVersion (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_configState_stagedIndexesFeatureVersionFour` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_configState_stateTransition_total` | counter | 3 | 0 | 1 | Scope (1), fromState (1), toState (1) | a counter: its rate over time; never the raw number |

## mongot_cursorManager (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_cursorManager_trackedCursors` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

## mongot_decoding (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_decoding_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decoding_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_decoding_executor_idle_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decoding_executor_idle_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_decoding_executor_idle_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decoding_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decoding_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decoding_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decoding_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decoding_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decoding_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decoding_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_decoding_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_decodingWorkScheduler (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_decodingWorkScheduler_decodingBatchDistribution_count` | summary | 3 | 3 | 3 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decodingWorkScheduler_decodingBatchDistribution_max` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decodingWorkScheduler_decodingBatchDistribution_sum` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decodingWorkScheduler_decodingBatchDurations_seconds_count` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decodingWorkScheduler_decodingBatchDurations_seconds_max` | gauge | 3 | 3 | 3 | Scope (1), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_decodingWorkScheduler_decodingBatchDurations_seconds_sum` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decodingWorkScheduler_decodingBatchSchedulingDurations_seconds_count` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decodingWorkScheduler_decodingBatchSchedulingDurations_seconds_max` | gauge | 3 | 3 | 3 | Scope (1), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_decodingWorkScheduler_decodingBatchSchedulingDurations_seconds_sum` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_decodingWorkScheduler_dequeueCalls_total` | counter | 3 | 3 | 3 |  | a counter: its rate over time; never the raw number |
| `mongot_decodingWorkScheduler_enqueueCalls_total` | counter | 3 | 3 | 3 |  | a counter: its rate over time; never the raw number |
| `mongot_decodingWorkScheduler_queuedBatchesTotal` | gauge | 6 | 0 | 1 | replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_decodingWorkScheduler_queuedEventsTotal` | gauge | 6 | 0 | 1 | replicationType (2) | constant, the same on every series: a number or a table row, not a line |

## mongot_disk (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_disk_monitor_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_disk_monitor_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_disk_monitor_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_disk_monitor_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_disk_monitor_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_disk_monitor_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_disk_monitor_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_disk_monitor_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_disk_monitor_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_disk_monitor_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_disk_monitor_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_disk_monitor_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_disk_monitor_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_disk_monitor_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_disk_monitor_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_diskUtilizationAwarenessMergePolicy (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_diskUtilizationAwarenessMergePolicy_discardedMerge_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |

## mongot_embedding (6)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_embedding_leasing_stats_mongodDiskFullErrors_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_embedding_leasing_stats_mongodSystemOverloadErrors_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_embedding_leasing_stats_mongodUserWritesBlockedErrors_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_embedding_materializedView_mongodDiskFullErrors_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_embedding_materializedView_mongodSystemOverloadErrors_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_embedding_materializedView_mongodUserWritesBlockedErrors_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |

## mongot_executor (2)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_executor_thread_allocatedBytes_bytes_total` | counter | 3 | 3 | 3 | name (1), subsystem (1) | a counter: its rate over time; never the raw number |
| `mongot_executor_thread_cpuTime_nanoseconds_total` | counter | 3 | 3 | 3 | name (1), subsystem (1) | a counter: its rate over time; never the raw number |

## mongot_ftdc (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_ftdc_reporter_executor_active_threads` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_ftdc_reporter_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_ftdc_reporter_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_ftdc_reporter_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_ftdc_reporter_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_ftdc_reporter_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_ftdc_reporter_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_ftdc_reporter_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_ftdc_reporter_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_ftdc_reporter_executor_queued_tasks` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_ftdc_reporter_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_ftdc_reporter_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_ftdc_reporter_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_ftdc_reporter_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_ftdc_reporter_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_grpc (2)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_grpc_health_check_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_grpc_health_check_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |

## mongot_guaranteed (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_guaranteed_blocking_server_worker_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_guaranteed_blocking_server_worker_executor_completed_tasks_total` | counter | 3 | 1 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_guaranteed_blocking_server_worker_executor_idle_seconds_count` | summary | 3 | 1 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_guaranteed_blocking_server_worker_executor_idle_seconds_max` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_guaranteed_blocking_server_worker_executor_idle_seconds_sum` | summary | 3 | 1 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_guaranteed_blocking_server_worker_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_guaranteed_blocking_server_worker_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_guaranteed_blocking_server_worker_executor_pool_size_threads` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_guaranteed_blocking_server_worker_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_guaranteed_blocking_server_worker_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_guaranteed_blocking_server_worker_executor_seconds_count` | summary | 3 | 1 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_guaranteed_blocking_server_worker_executor_seconds_max` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_guaranteed_blocking_server_worker_executor_seconds_sum` | summary | 3 | 1 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_idle (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_idle_cursor_killer_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_idle_cursor_killer_executor_completed_tasks_total` | counter | 3 | 3 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_idle_cursor_killer_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_idle_cursor_killer_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_idle_cursor_killer_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_idle_cursor_killer_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_idle_cursor_killer_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_idle_cursor_killer_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_idle_cursor_killer_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_idle_cursor_killer_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_idle_cursor_killer_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_idle_cursor_killer_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_idle_cursor_killer_executor_seconds_count` | summary | 3 | 3 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_idle_cursor_killer_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_idle_cursor_killer_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_index (204)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_index_commit_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_commit_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_index_commit_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_commit_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_commit_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_commit_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_commit_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_commit_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_commit_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_commit_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_commit_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_index_commit_executor_scheduled_repetitively_total` | counter | 3 | 0 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_index_commit_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_commit_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_index_commit_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_lifecycle_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_index_lifecycle_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_lifecycle_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_idle_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_lifecycle_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_lifecycle_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_lifecycle_executor_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_refresh_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_refresh_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_index_refresh_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_refresh_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_refresh_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_refresh_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_refresh_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_refresh_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_refresh_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_refresh_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_refresh_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_index_refresh_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_index_refresh_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_refresh_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_index_refresh_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_indexFeatureVersion` | gauge | 15 | 0 | 1 | generationId_logString (5), indexId_logString (5) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_indexSizeBytes` | gauge | 15 | 0 | 5 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), numPartitions (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_index_stats_indexStatusCode` | gauge | 135 | 0 | 2 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), status (9) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_index_stats_indexing_bloomFilterIdPostingCreated_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_commitDurations_seconds` | summary | 60 | 40 | 12 | generationId_logString (5), indexId_logString (5), quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_indexing_commitDurations_seconds_count` | summary | 15 | 15 | 2 | generationId_logString (5), indexId_logString (5), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_indexing_commitDurations_seconds_max` | gauge | 15 | 15 | 15 | generationId_logString (5), indexId_logString (5), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_indexing_commitDurations_seconds_sum` | summary | 15 | 15 | 15 | generationId_logString (5), indexId_logString (5), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_indexing_consecutiveInitialSyncResyncExceptions` | gauge | 15 | 0 | 1 | generationId_logString (5), indexId_logString (5) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_indexing_delete_total` | counter | 15 | 0 | 1 | generationId_logString (5), indexId_logString (5), indexType (2) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_indexingBatchDurations_seconds_count` | summary | 6 | 6 | 6 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_indexing_indexingBatchDurations_seconds_max` | gauge | 6 | 6 | 6 | indexType (2), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_indexing_indexingBatchDurations_seconds_sum` | summary | 6 | 6 | 6 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_indexing_initialSyncExceptions_total` | counter | 15 | 0 | 1 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_insert_total` | counter | 15 | 0 | 3 | generationId_logString (5), indexId_logString (5), indexType (2) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_invalidGeometryField_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_largeChangeStreamEvents_total` | counter | 12 | 0 | 1 | threshold (4) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_lucene99IdPostingCreated_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_maxPossibleReplicationOpTime` | gauge | 15 | 15 | 1 | generationId_logString (5), indexId_logString (5) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_indexing_replicationLagMs` | gauge | 15 | 8 | 1 | generationId_logString (5), indexId_logString (5), indexType (2) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_indexing_replicationOpTime` | gauge | 15 | 15 | 1 | generationId_logString (5), indexId_logString (5) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_indexing_sortableStringTruncated_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_steadyStateExceptions_total` | counter | 15 | 0 | 1 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_totalBytesProcessed_total` | counter | 15 | 0 | 5 | generationId_logString (5), indexId_logString (5) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_update_total` | counter | 15 | 0 | 1 | generationId_logString (5), indexId_logString (5), indexType (2) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_indexing_vectorFieldsIndexed_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_largestIndexFileSizeBytes` | gauge | 15 | 0 | 5 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), numPartitions (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_index_stats_luceneIndexRefresher_refreshDurations_seconds` | summary | 60 | 60 | 52 | generationId_logString (5), indexId_logString (5), quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_luceneIndexRefresher_refreshDurations_seconds_count` | summary | 15 | 15 | 10 | generationId_logString (5), indexId_logString (5), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_luceneIndexRefresher_refreshDurations_seconds_max` | gauge | 15 | 15 | 15 | generationId_logString (5), indexId_logString (5), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_luceneIndexRefresher_refreshDurations_seconds_sum` | summary | 15 | 15 | 15 | generationId_logString (5), indexId_logString (5), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_numFilesInIndex` | gauge | 15 | 0 | 1 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), numPartitions (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_numLuceneDocs` | gauge | 15 | 0 | 3 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), numPartitions (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_index_stats_numLuceneFields` | gauge | 15 | 0 | 4 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), numPartitions (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_index_stats_numLuceneMaxDocs` | gauge | 15 | 0 | 3 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), numPartitions (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_index_stats_query_batchDataSize` | summary | 12 | 12 | 2 | quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_batchDataSize_count` | summary | 3 | 3 | 3 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_batchDataSize_max` | gauge | 3 | 3 | 1 |  | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_batchDataSize_sum` | summary | 3 | 3 | 3 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_batchDocumentCount` | summary | 12 | 12 | 2 | quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_batchDocumentCount_count` | summary | 3 | 3 | 3 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_batchDocumentCount_max` | gauge | 3 | 3 | 1 |  | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_batchDocumentCount_sum` | summary | 3 | 3 | 3 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_batchWithTies_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_benefitFromIndexSortCount_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_dynamicFeatureFlagLatencies_seconds_count` | summary | 3 | 3 | 3 | evaluationResult (1), featureFlagName (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_dynamicFeatureFlagLatencies_seconds_max` | gauge | 3 | 3 | 3 | evaluationResult (1), featureFlagName (1), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_dynamicFeatureFlagLatencies_seconds_sum` | summary | 3 | 3 | 3 | evaluationResult (1), featureFlagName (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_extractableLimitQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_extractableLimitSecondBatchQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_failedExplainQueryAggregate_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_failedQueries_total` | counter | 15 | 0 | 1 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_fallBackHeuristicFailureCounter_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_fallBackHeuristicSuccessCounter_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_feature_total` | counter | 432 | 16 | 7 | name (144 !) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_getMoreCommandCallsPerQuery` | summary | 12 | 12 | 1 | quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_getMoreCommandCallsPerQuery_count` | summary | 3 | 3 | 2 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_getMoreCommandCallsPerQuery_max` | gauge | 3 | 3 | 1 |  | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_getMoreCommandCallsPerQuery_sum` | summary | 3 | 3 | 2 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_getMoreCommandCalls_total` | counter | 9 | 6 | 5 | generationId_logString (3), indexId_logString (3) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_internallyFailedQueries_total` | counter | 3 | 0 | 1 | indexFeatureVersion (1) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_invalidQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_knnSearchMode_total` | counter | 12 | 3 | 4 | mode (4) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_lenientFailures_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_limitPerQuery_bucket` | histogram | 21 | 21 | 3 | le (7) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_limitPerQuery_count` | histogram | 3 | 3 | 3 |  | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_limitPerQuery_max` | gauge | 3 | 3 | 1 |  | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_limitPerQuery_sum` | histogram | 3 | 3 | 3 |  | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_luceneTopDocsSearchLatencies_seconds` | summary | 12 | 12 | 10 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_luceneTopDocsSearchLatencies_seconds_count` | summary | 3 | 3 | 2 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_luceneTopDocsSearchLatencies_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_luceneTopDocsSearchLatencies_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_noProgressBatches_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_npeQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_numCandidatesPerQuery_bucket` | histogram | 63 | 21 | 7 | le (7), quantization (3) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_numCandidatesPerQuery_count` | histogram | 9 | 3 | 4 | quantization (3) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_numCandidatesPerQuery_max` | gauge | 9 | 3 | 2 | quantization (3) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_numCandidatesPerQuery_sum` | histogram | 9 | 3 | 4 | quantization (3) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_orphanedDeletedDocsRatio` | summary | 12 | 0 | 1 | quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_orphanedDeletedDocsRatio_count` | summary | 3 | 0 | 1 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_orphanedDeletedDocsRatio_max` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_query_orphanedDeletedDocsRatio_sum` | summary | 3 | 0 | 1 |  | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_phantomSearcherCleanupCount_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_searchResultBatchLatencies_seconds` | summary | 36 | 24 | 9 | generationId_logString (3), indexFeatureVersion (1), indexId_logString (3), quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_searchResultBatchLatencies_seconds_count` | summary | 9 | 6 | 5 | generationId_logString (3), indexFeatureVersion (1), indexId_logString (3), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_searchResultBatchLatencies_seconds_max` | gauge | 9 | 6 | 4 | generationId_logString (3), indexFeatureVersion (1), indexId_logString (3), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_searchResultBatchLatencies_seconds_sum` | summary | 9 | 6 | 7 | generationId_logString (3), indexFeatureVersion (1), indexId_logString (3), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_stringFacetsStateRefreshLatency_seconds` | summary | 36 | 0 | 1 | generationId_logString (3), indexId_logString (3), quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_stringFacetsStateRefreshLatency_seconds_count` | summary | 9 | 0 | 1 | generationId_logString (3), indexId_logString (3), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_stringFacetsStateRefreshLatency_seconds_max` | gauge | 9 | 0 | 1 | generationId_logString (3), indexId_logString (3), timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_query_stringFacetsStateRefreshLatency_seconds_sum` | summary | 9 | 0 | 1 | generationId_logString (3), indexId_logString (3), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_tokenFacetsStateRefreshLatency_seconds` | summary | 36 | 24 | 9 | generationId_logString (3), indexId_logString (3), quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_tokenFacetsStateRefreshLatency_seconds_count` | summary | 9 | 9 | 2 | generationId_logString (3), indexId_logString (3), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_tokenFacetsStateRefreshLatency_seconds_max` | gauge | 9 | 9 | 9 | generationId_logString (3), indexId_logString (3), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_tokenFacetsStateRefreshLatency_seconds_sum` | summary | 9 | 9 | 9 | generationId_logString (3), indexId_logString (3), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_totalFacetBucketsPerQuery_bucket` | histogram | 12 | 0 | 1 | le (4) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_totalFacetBucketsPerQuery_count` | histogram | 3 | 0 | 1 |  | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_totalFacetBucketsPerQuery_max` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_query_totalFacetBucketsPerQuery_sum` | histogram | 3 | 0 | 1 |  | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_totalHitsCount_total` | counter | 3 | 3 | 3 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_totalQueries_total` | counter | 15 | 12 | 11 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_vectorCommandCalls_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_vectorRescoringFailureCount_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_vectorResultLatencies_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorResultLatencies_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorResultLatencies_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_query_vectorResultLatencies_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorSearchGetMoreTopDocsLatencyTimer_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorSearchGetMoreTopDocsLatencyTimer_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorSearchGetMoreTopDocsLatencyTimer_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_query_vectorSearchGetMoreTopDocsLatencyTimer_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorSearchInitialTopDocsLatencyTimer_seconds` | summary | 12 | 12 | 6 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorSearchInitialTopDocsLatencyTimer_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorSearchInitialTopDocsLatencyTimer_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_vectorSearchInitialTopDocsLatencyTimer_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_query_vectorSearchQueriesOverSearchIndexes_total` | counter | 15 | 0 | 1 | generationId_logString (5), indexId_logString (5) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_query_vectorSearchVisitedNodesPerSegment_bucket` | histogram | 96 | 24 | 6 | filter (2), le (8), mode (2) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_vectorSearchVisitedNodesPerSegment_count` | histogram | 12 | 3 | 4 | filter (2), mode (2) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_vectorSearchVisitedNodesPerSegment_max` | gauge | 12 | 3 | 2 | filter (2), mode (2) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_query_vectorSearchVisitedNodesPerSegment_sum` | histogram | 12 | 3 | 4 | filter (2), mode (2) | a distribution: a percentile from its buckets, across instances |
| `mongot_index_stats_query_vectorSearchVisitedNodes_total` | counter | 12 | 4 | 5 | filter (2), mode (2) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableBytes` | summary | 24 | 0 | 1 | indexType (2), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableBytes_count` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableBytes_max` | gauge | 6 | 0 | 1 | indexType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableBytes_sum` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableDocuments` | summary | 24 | 0 | 1 | indexType (2), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableDocuments_count` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableDocuments_max` | gauge | 6 | 0 | 1 | indexType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_initialSync_changeStream_batchTotalApplicableDocuments_sum` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_changeStream_getMoreDurations_seconds_count` | summary | 6 | 0 | 2 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_changeStream_getMoreDurations_seconds_max` | gauge | 6 | 0 | 1 | indexType (2), timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_initialSync_changeStream_getMoreDurations_seconds_sum` | summary | 6 | 0 | 2 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableBytes` | summary | 24 | 0 | 1 | indexType (2), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableBytes_count` | summary | 6 | 0 | 2 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableBytes_max` | gauge | 6 | 0 | 1 | indexType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableBytes_sum` | summary | 6 | 0 | 2 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableDocuments` | summary | 24 | 0 | 1 | indexType (2), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableDocuments_count` | summary | 6 | 0 | 2 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableDocuments_max` | gauge | 6 | 0 | 1 | indexType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_initialSync_collScan_batchTotalApplicableDocuments_sum` | summary | 6 | 0 | 2 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_getMoreDurations_seconds_count` | summary | 6 | 0 | 1 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_collScan_getMoreDurations_seconds_max` | gauge | 6 | 0 | 1 | indexType (2), timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_initialSync_collScan_getMoreDurations_seconds_sum` | summary | 6 | 0 | 6 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_initialSync_idFieldType` | gauge | 15 | 0 | 1 | bsonType (1), generationId_logString (5), indexId_logString (5), indexType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_initialSync_totalApplicableBytes_total` | counter | 6 | 0 | 2 | indexType (2) | a counter: its rate over time; never the raw number |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableBytes` | summary | 24 | 0 | 1 | indexType (2), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableBytes_count` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableBytes_max` | gauge | 6 | 0 | 1 | indexType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableBytes_sum` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableDocuments` | summary | 24 | 0 | 1 | indexType (2), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableDocuments_count` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableDocuments_max` | gauge | 6 | 0 | 1 | indexType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_index_stats_replication_steadyState_batchTotalApplicableDocuments_sum` | summary | 6 | 0 | 1 | indexType (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_decodingBatchDurations_seconds_count` | summary | 6 | 6 | 6 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_decodingBatchDurations_seconds_max` | gauge | 6 | 6 | 6 | indexType (2), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_replication_steadyState_decodingBatchDurations_seconds_sum` | summary | 6 | 6 | 6 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_getMoreDurations_seconds_count` | summary | 6 | 6 | 6 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_replication_steadyState_getMoreDurations_seconds_max` | gauge | 6 | 6 | 6 | indexType (2), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_index_stats_replication_steadyState_getMoreDurations_seconds_sum` | summary | 6 | 6 | 6 | indexType (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_index_stats_requiredMemoryBytes` | gauge | 15 | 0 | 3 | generationId_logString (5), indexFeatureVersion (1), indexId_logString (5), numPartitions (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_index_stats_segment_count` | gauge | 15 | 0 | 1 | generationId_logString (5), indexId_logString (5) | constant, the same on every series: a number or a table row, not a line |

## mongot_indexFactory (3)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_indexFactory_cacheWarmerTotalMilliseconds_seconds` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexFactory_unreadableDroppedIndexes_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_indexFactory_unreadableIndexRecoveries_total` | counter | 9 | 0 | 1 | unreadableIndexCause (3) | a counter: its rate over time; never the raw number |

## mongot_indexing (77)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_indexing_auto_embedding_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_indexing_auto_embedding_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_auto_embedding_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_auto_embedding_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_auto_embedding_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_auto_embedding_executor_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_changeStreamModeSelector_failedSamplingAttemptsCounter_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_indexing_initialSyncChangeStream_getMoreDurations_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncChangeStream_getMoreDurations_seconds_count` | summary | 3 | 0 | 2 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncChangeStream_getMoreDurations_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_initialSyncChangeStream_getMoreDurations_seconds_sum` | summary | 3 | 0 | 2 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncCollectionScan_getMoreDurations_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncCollectionScan_getMoreDurations_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncCollectionScan_getMoreDurations_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_initialSyncCollectionScan_getMoreDurations_seconds_sum` | summary | 3 | 0 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncCollectionScan_openScanDurations_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncCollectionScan_openScanDurations_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_initialSyncCollectionScan_openScanDurations_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_initialSyncCollectionScan_openScanDurations_seconds_sum` | summary | 3 | 0 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_lifecycle_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_completed_tasks_total` | counter | 3 | 0 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_indexing_lifecycle_executor_idle_seconds_count` | summary | 3 | 0 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_lifecycle_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_idle_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_lifecycle_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_seconds_count` | summary | 3 | 0 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_lifecycle_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_lifecycle_executor_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_applicableChangeStreamUpdates_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_indexing_steadyStateChangeStream_batchesInProgressTotal` | gauge | 18 | 6 | 2 | indexType (3), replicationType (2) | a level that moves: a line over time; a number for now |
| `mongot_indexing_steadyStateChangeStream_batchesInProgressTotalDurations_seconds` | summary | 12 | 4 | 2 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_batchesInProgressTotalDurations_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_batchesInProgressTotalDurations_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_indexing_steadyStateChangeStream_batchesInProgressTotalDurations_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_dispatcher` | gauge | 6 | 0 | 1 | Scope (1), client (1), replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_steadyStateChangeStream_getMoreDurations_seconds` | summary | 12 | 3 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_getMoreDurations_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_getMoreDurations_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_indexing_steadyStateChangeStream_getMoreDurations_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_getMoresInFlight` | gauge | 6 | 0 | 2 | replicationType (2) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_indexing_steadyStateChangeStream_getMoresScheduled` | gauge | 18 | 6 | 3 | indexType (3), replicationType (2) | a level that moves: a line over time; a number for now |
| `mongot_indexing_steadyStateChangeStream_getMoresSchedulingDurations_seconds` | summary | 12 | 10 | 4 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_getMoresSchedulingDurations_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_getMoresSchedulingDurations_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_indexing_steadyStateChangeStream_getMoresSchedulingDurations_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_preprocessingBatchDurations_seconds` | summary | 12 | 12 | 8 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_preprocessingBatchDurations_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_preprocessingBatchDurations_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_indexing_steadyStateChangeStream_preprocessingBatchDurations_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_steadyStateChangeStream_rescheduledEmbeddingGetMores_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_indexing_steadyStateChangeStream_skippedChangeStreamDocumentsWithoutMetadataNamespace_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_indexing_steadyStateChangeStream_unexpectedBatchFailures_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_indexing_steadyStateChangeStream_witnessedChangeStreamUpdates_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_indexing_work_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_work_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_indexing_work_executor_idle_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_work_executor_idle_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_indexing_work_executor_idle_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_work_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_work_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_work_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_work_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_work_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexing_work_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexing_work_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_indexing_work_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_indexingWorkScheduler (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_indexingWorkScheduler_dequeueCalls_total` | counter | 3 | 3 | 3 |  | a counter: its rate over time; never the raw number |
| `mongot_indexingWorkScheduler_enqueueCalls_total` | counter | 3 | 3 | 3 |  | a counter: its rate over time; never the raw number |
| `mongot_indexingWorkScheduler_indexingBatchDistribution_count` | summary | 3 | 3 | 3 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexingWorkScheduler_indexingBatchDistribution_max` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexingWorkScheduler_indexingBatchDistribution_sum` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexingWorkScheduler_indexingBatchDurations_seconds_count` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexingWorkScheduler_indexingBatchDurations_seconds_max` | gauge | 3 | 3 | 3 | Scope (1), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_indexingWorkScheduler_indexingBatchDurations_seconds_sum` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexingWorkScheduler_indexingBatchSchedulingDurations_seconds_count` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexingWorkScheduler_indexingBatchSchedulingDurations_seconds_max` | gauge | 3 | 3 | 3 | Scope (1), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_indexingWorkScheduler_indexingBatchSchedulingDurations_seconds_sum` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_indexingWorkScheduler_queuedBatchesTotal` | gauge | 3 | 0 | 1 | replicationType (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_indexingWorkScheduler_queuedEventsTotal` | gauge | 3 | 0 | 1 | replicationType (1) | constant, the same on every series: a number or a table row, not a line |

## mongot_init (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_init_lifecycle_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_init_lifecycle_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_init_lifecycle_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_idle_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_init_lifecycle_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_init_lifecycle_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_init_lifecycle_executor_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_initialSyncManager (28)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_initialSyncManager_applicableInitialSyncUpdates_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_initialSyncManager_changeStreamPreprocessingBatchDurations_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_changeStreamPreprocessingBatchDurations_seconds_count` | summary | 3 | 0 | 2 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_changeStreamPreprocessingBatchDurations_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialSyncManager_changeStreamPreprocessingBatchDurations_seconds_sum` | summary | 3 | 0 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_changeStreamTime_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_changeStreamTime_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_changeStreamTime_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialSyncManager_changeStreamTime_seconds_sum` | summary | 3 | 0 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_changeStreamTotalDocuments_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_initialSyncManager_collectionScanPreprocessingBatchDurations_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_collectionScanPreprocessingBatchDurations_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_collectionScanPreprocessingBatchDurations_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialSyncManager_collectionScanPreprocessingBatchDurations_seconds_sum` | summary | 3 | 0 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_collectionScanTime_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_collectionScanTime_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_collectionScanTime_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialSyncManager_collectionScanTime_seconds_sum` | summary | 3 | 0 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_completedSyncThroughputBytesPerSec_bucket` | histogram | 24 | 0 | 3 | le (8), sizeCategory (1) | a distribution: a percentile from its buckets, across instances |
| `mongot_initialSyncManager_completedSyncThroughputBytesPerSec_count` | histogram | 3 | 0 | 1 | sizeCategory (1) | a distribution: a percentile from its buckets, across instances |
| `mongot_initialSyncManager_completedSyncThroughputBytesPerSec_max` | gauge | 3 | 0 | 1 | sizeCategory (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialSyncManager_completedSyncThroughputBytesPerSec_sum` | histogram | 3 | 0 | 3 | sizeCategory (1) | a distribution: a percentile from its buckets, across instances |
| `mongot_initialSyncManager_fsyncDuration_seconds_count` | summary | 6 | 0 | 1 | outcome (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_fsyncDuration_seconds_max` | gauge | 6 | 0 | 1 | outcome (2), timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialSyncManager_fsyncDuration_seconds_sum` | summary | 6 | 0 | 1 | outcome (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialSyncManager_skippedDocumentsWithoutMetadataNamespace_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_initialSyncManager_skippedInitialSyncDocumentsWithoutMetadataNamespace_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_initialSyncManager_witnessedInitialSyncUpdates_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |

## mongot_initialsync (18)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_initialsync_dispatcher_collectionScan_total` | counter | 12 | 0 | 2 | replicationType (2), scan_type (2) | a counter: its rate over time; never the raw number |
| `mongot_initialsync_dispatcher_completedSyncDuration_seconds_count` | summary | 6 | 0 | 2 | scan_type (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialsync_dispatcher_completedSyncDuration_seconds_max` | gauge | 6 | 0 | 1 | scan_type (2), timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_completedSyncDuration_seconds_sum` | summary | 6 | 0 | 4 | scan_type (2), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialsync_dispatcher_inProgressInitialSyncDurationMax_seconds` | gauge | 6 | 0 | 1 | replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_inProgressInitialSyncDurationMin_seconds` | gauge | 6 | 0 | 1 | replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_inProgressInitialSyncDurationSum_seconds` | gauge | 6 | 0 | 1 | replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_inProgressResumedSyncs` | gauge | 6 | 0 | 1 | replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_inProgressSyncs` | gauge | 18 | 0 | 1 | indexType (3), replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_queuedSyncs` | gauge | 6 | 0 | 1 | replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_syncDuration_seconds_count` | summary | 6 | 0 | 1 | scan_type (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialsync_dispatcher_syncDuration_seconds_max` | gauge | 6 | 0 | 1 | scan_type (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_dispatcher_syncDuration_seconds_sum` | summary | 6 | 0 | 1 | scan_type (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_initialsync_dispatcher_syncSource_total` | counter | 3 | 0 | 1 | hostName (1) | a counter: its rate over time; never the raw number |
| `mongot_initialsync_dispatcher_unreadableDroppedIndexes_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_initialsync_dispatcher_unreadableIndexRecoveries_total` | counter | 9 | 0 | 1 | unreadableIndexCause (3) | a counter: its rate over time; never the raw number |
| `mongot_initialsync_queue_queuedSyncs` | gauge | 18 | 0 | 1 | indexType (3), replicationType (2) | constant, the same on every series: a number or a table row, not a line |
| `mongot_initialsync_queue_requeuedEmbeddingInitialSyncs_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |

## mongot_jvm (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_jvm_buffer_count_buffers` | gauge | 9 | 0 | 5 | Scope (1), id (3) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_jvm_buffer_memory_used_bytes` | gauge | 9 | 3 | 5 | Scope (1), id (3) | a level that moves: a line over time; a number for now |
| `mongot_jvm_buffer_total_capacity_bytes` | gauge | 9 | 3 | 5 | Scope (1), id (3) | a level that moves: a line over time; a number for now |
| `mongot_jvm_gc_live_data_size_bytes` | gauge | 3 | 0 | 3 | Scope (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_jvm_gc_max_data_size_bytes` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_jvm_gc_memory_allocated_bytes_total` | counter | 3 | 3 | 3 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_jvm_gc_memory_promoted_bytes_total` | counter | 3 | 3 | 3 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_jvm_gc_pause_seconds_count` | summary | 10 | 3 | 5 | Scope (1), action (2), cause (4), gc (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_jvm_gc_pause_seconds_max` | gauge | 10 | 3 | 3 | Scope (1), action (2), cause (4), gc (2) | a level that moves: a line over time; a number for now |
| `mongot_jvm_gc_pause_seconds_sum` | summary | 10 | 3 | 10 | Scope (1), action (2), cause (4), gc (2) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_jvm_memory_committed_bytes` | gauge | 24 | 8 | 14 | Scope (1), area (2), id (8) | a level that moves: a line over time; a number for now |
| `mongot_jvm_memory_max_bytes` | gauge | 24 | 0 | 8 | Scope (1), area (2), id (8) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_jvm_memory_used_bytes` | gauge | 24 | 21 | 24 | Scope (1), area (2), id (8) | a level that moves: a line over time; a number for now |

## mongot_lifecycle (8)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_lifecycle_failedDownloadIndexes_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_lifecycle_failedDropIndexes_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_lifecycle_failedInitializationIndexes_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_lifecycle_indexInitializationDuration_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_lifecycle_indexInitializationDuration_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_lifecycle_indexInitializationDuration_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_lifecycle_indexInitializationDuration_seconds_sum` | summary | 3 | 0 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_lifecycle_indexesInInitializedState` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

## mongot_loadShedding (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_loadShedding_skippedDueToCancelledStream_total` | counter | 3 | 0 | 1 | executor (1) | a counter: its rate over time; never the raw number |

## mongot_mat (60)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_mat_view_leader_heartbeat_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_leader_heartbeat_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_leader_heartbeat_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_leader_heartbeat_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_leader_heartbeat_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_leader_heartbeat_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_leader_heartbeat_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_leader_heartbeat_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_leader_heartbeat_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_leader_heartbeat_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_leader_heartbeat_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_leader_heartbeat_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_leader_heartbeat_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_leader_heartbeat_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_mat_view_leader_heartbeat_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_optime_updater_executor_active_threads` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_mat_view_optime_updater_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_optime_updater_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_optime_updater_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_optime_updater_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_optime_updater_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_optime_updater_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_optime_updater_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_optime_updater_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_optime_updater_executor_queued_tasks` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_mat_view_optime_updater_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_optime_updater_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_optime_updater_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_optime_updater_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_mat_view_optime_updater_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_stale_lease_scanner_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_stale_lease_scanner_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_stale_lease_scanner_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_stale_lease_scanner_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_stale_lease_scanner_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_stale_lease_scanner_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_stale_lease_scanner_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_stale_lease_scanner_executor_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_status_refresh_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_status_refresh_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_status_refresh_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_status_refresh_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_status_refresh_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_status_refresh_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_status_refresh_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_status_refresh_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_status_refresh_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_status_refresh_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mat_view_status_refresh_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_status_refresh_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mat_view_status_refresh_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mat_view_status_refresh_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_mat_view_status_refresh_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_materialized (13)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_materialized_view_lifecycle_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_completed_tasks_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_materialized_view_lifecycle_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_materialized_view_lifecycle_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_materialized_view_lifecycle_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_materialized_view_lifecycle_executor_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_materialized_view_lifecycle_executor_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_materializedView (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_materializedView_replication_manager` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

## mongot_mergeScheduler (23)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_mergeScheduler_currentlyMergingDocs` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mergeScheduler_currentlyRunningMerges` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mergeScheduler_mergeCancellationTime_seconds_count` | summary | 3 | 0 | 1 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeCancellationTime_seconds_max` | gauge | 3 | 0 | 1 | Scope (1), timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mergeScheduler_mergeCancellationTime_seconds_sum` | summary | 3 | 0 | 1 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeResultSize` | summary | 12 | 0 | 1 | Scope (1), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeResultSize_count` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeResultSize_max` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mergeScheduler_mergeResultSize_sum` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeSize` | summary | 12 | 0 | 1 | Scope (1), quantile (4) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeSize_count` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeSize_max` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mergeScheduler_mergeSize_sum` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeTime_seconds_count` | summary | 3 | 0 | 1 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergeTime_seconds_max` | gauge | 3 | 0 | 1 | Scope (1), timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mergeScheduler_mergeTime_seconds_sum` | summary | 3 | 0 | 1 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergedDocs_count` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_mergedDocs_max` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mergeScheduler_mergedDocs_sum` | summary | 3 | 0 | 1 | Scope (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mergeScheduler_numMergePauseEvents_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_mergeScheduler_numMergesAborted_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_mergeScheduler_numMerges_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_mergeScheduler_numSegmentsMerged_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |

## mongot_metadata (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_metadata_updater_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_metadata_updater_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_metadata_updater_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_metadata_updater_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_metadata_updater_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_metadata_updater_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_metadata_updater_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_metadata_updater_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_metadata_updater_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_metadata_updater_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_metadata_updater_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_metadata_updater_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_metadata_updater_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_metadata_updater_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_metadata_updater_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_mongoClient (4)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_mongoClient_connectionPool_connections` | gauge | 33 | 0 | 6 | Scope (1), clientName (11) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_mongoClient_connectionPool_connectionsCheckedOut` | gauge | 33 | 1 | 2 | Scope (1), clientName (11) | a level that moves: a line over time; a number for now |
| `mongot_mongoClient_connectionPool_maxSize` | gauge | 33 | 0 | 5 | Scope (1), clientName (11) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_mongoClient_connectionPool_minSize` | gauge | 33 | 0 | 1 | Scope (1), clientName (11) | constant, the same on every series: a number or a table row, not a line |

## mongot_mongoClientBuilder (2)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_mongoClientBuilder_failedOpenSSLDynamicLinking_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_mongoClientBuilder_successfulOpenSSLDynamicLinking_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |

## mongot_mongod (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_mongod_topology_monitor_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mongod_topology_monitor_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mongod_topology_monitor_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mongod_topology_monitor_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mongod_topology_monitor_executor_idle_seconds_sum` | summary | 3 | 0 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mongod_topology_monitor_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mongod_topology_monitor_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mongod_topology_monitor_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mongod_topology_monitor_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mongod_topology_monitor_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_mongod_topology_monitor_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mongod_topology_monitor_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_mongod_topology_monitor_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_mongod_topology_monitor_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_mongod_topology_monitor_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_mongodb (2)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_mongodb_syncSourceChange_total` | counter | 2 | 0 | 1 | type (1) | a counter: its rate over time; never the raw number |
| `mongot_mongodb_version` | gauge | 3 | 0 | 1 | version (1) | constant, the same on every series: a number or a table row, not a line |

## mongot_process (4)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_process_cpu_time_ns_total` | counter | 3 | 3 | 3 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_process_cpu_usage` | gauge | 3 | 3 | 3 | Scope (1) | a level that moves: a line over time; a number for now |
| `mongot_process_start_time_seconds` | gauge | 3 | 0 | 3 | Scope (1) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_process_uptime_seconds` | gauge | 3 | 3 | 3 | Scope (1) | a level that moves: a line over time; a number for now |

## mongot_prometheus (4)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_prometheus_server_scraping_timer_seconds` | summary | 12 | 12 | 10 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_prometheus_server_scraping_timer_seconds_count` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_prometheus_server_scraping_timer_seconds_max` | gauge | 3 | 3 | 3 | timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_prometheus_server_scraping_timer_seconds_sum` | summary | 3 | 3 | 3 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_readiness (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_readiness_lifecycleInitialized` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

## mongot_rejectedConcurrentSearchExecutionCount (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_rejectedConcurrentSearchExecutionCount_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |

## mongot_rejectedConcurrentVectorRescoringExecutionCount (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_rejectedConcurrentVectorRescoringExecutionCount_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |

## mongot_replication (10)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_replication_manager` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_replication_mongodb_indexManagerState` | gauge | 24 | 0 | 2 | state (8) | constant, differing by series: a table or sorted bars, not a line |
| `mongot_replication_mongodb_manager` | gauge | 3 | 0 | 1 | type (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_replication_mongodb_matViewGeneratorState` | gauge | 24 | 0 | 1 | state (8) | constant, the same on every series: a number or a table row, not a line |
| `mongot_replication_sessionRefresher_failedSessionRefreshes_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_replication_sessionRefresher_refreshes_total` | counter | 3 | 3 | 2 |  | a counter: its rate over time; never the raw number |
| `mongot_replication_sessionRefresher_sessionRefreshDurations_seconds_count` | summary | 3 | 3 | 2 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_replication_sessionRefresher_sessionRefreshDurations_seconds_max` | gauge | 3 | 3 | 1 | Scope (1), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_replication_sessionRefresher_sessionRefreshDurations_seconds_sum` | summary | 3 | 3 | 3 | Scope (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_replication_sessionRefresher_sessions` | gauge | 6 | 1 | 2 | replicationType (2) | a level that moves: a line over time; a number for now |

## mongot_replicationIndexManager (2)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_replicationIndexManager_exceptions_total` | counter | 2 | 0 | 1 | cause (1), causeCategory (1), clazz (1), type (1) | a counter: its rate over time; never the raw number |
| `mongot_replicationIndexManager_transitionState_total` | counter | 10 | 0 | 1 | fromState (3), toState (3) | a counter: its rate over time; never the raw number |

## mongot_replicationOptimeUpdater (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_replicationOptimeUpdater_executor_active_threads` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_replicationOptimeUpdater_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_replicationOptimeUpdater_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_replicationOptimeUpdater_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_replicationOptimeUpdater_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_replicationOptimeUpdater_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_replicationOptimeUpdater_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_replicationOptimeUpdater_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_replicationOptimeUpdater_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_replicationOptimeUpdater_executor_queued_tasks` | gauge | 3 | 1 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_replicationOptimeUpdater_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_replicationOptimeUpdater_executor_scheduled_repetitively_total` | counter | 3 | 0 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_replicationOptimeUpdater_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_replicationOptimeUpdater_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_replicationOptimeUpdater_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_replicationOptimeUpdaterError (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_replicationOptimeUpdaterError_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |

## mongot_search (27)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_search_metrics_approximateVectorSearchQueries_total` | counter | 3 | 3 | 3 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_autoEmbeddingMultiModalVectorSearchQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_autoEmbeddingTextVectorSearchQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_autoEmbeddingVectorSearchQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_bsonBitVectorQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_bsonByteVectorQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_bsonFloatVectorQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_concurrentApproximateQueries` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_search_metrics_concurrentAutoEmbeddingQueries` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_search_metrics_concurrentExactQueries` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_search_metrics_exactVectorSearchQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_nestedVectorSearchQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_queriesAgainstViewSourceCollection_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_queriesAgainstView_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_searchCommandInvalidQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_searchCommandTotalCount_total` | counter | 3 | 3 | 2 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_searchCommandWrappedInvalidQueryException_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_vectorQueriesTimedOut_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_vectorQueriesWithDeadline_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_vectorSearchCommandInvalidQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_vectorSearchCommandTotalCount_total` | counter | 3 | 3 | 3 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_vectorSearchCommandTotalLatencyByIndexSize_seconds` | summary | 12 | 12 | 6 | indexSizeCategory (1), isNested (1), quantile (4), quantizationType (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_search_metrics_vectorSearchCommandTotalLatencyByIndexSize_seconds_count` | summary | 3 | 3 | 3 | indexSizeCategory (1), isNested (1), quantizationType (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_search_metrics_vectorSearchCommandTotalLatencyByIndexSize_seconds_max` | gauge | 3 | 3 | 3 | indexSizeCategory (1), isNested (1), quantizationType (1), timeUnit (1) | a level that moves: a line over time; a number for now |
| `mongot_search_metrics_vectorSearchCommandTotalLatencyByIndexSize_seconds_sum` | summary | 3 | 3 | 3 | indexSizeCategory (1), isNested (1), quantizationType (1), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_search_metrics_vectorSearchCommandWrappedInvalidQueryException_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_search_metrics_vectorStoredSourceQueries_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |

## mongot_session (15)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_session_refresh_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_session_refresh_executor_completed_tasks_total` | counter | 3 | 3 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_session_refresh_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_session_refresh_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_session_refresh_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_session_refresh_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_session_refresh_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_session_refresh_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_session_refresh_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_session_refresh_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_session_refresh_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_session_refresh_executor_scheduled_repetitively_total` | counter | 3 | 0 | 2 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_session_refresh_executor_seconds_count` | summary | 3 | 3 | 2 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_session_refresh_executor_seconds_max` | gauge | 3 | 3 | 1 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_session_refresh_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_synonymSync (12)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_synonymSync_collScanDurations_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_synonymSync_collScanDurations_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_synonymSync_collScanDurations_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_synonymSync_collScanDurations_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_synonymSync_collScansTriggeredByChangeStream_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_synonymSync_collScans_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_synonymSync_exceptions_total` | counter | 3 | 0 | 1 |  | a counter: its rate over time; never the raw number |
| `mongot_synonymSync_queueDepth` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_synonymSync_syncDurations_seconds` | summary | 12 | 0 | 1 | quantile (4), timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_synonymSync_syncDurations_seconds_count` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_synonymSync_syncDurations_seconds_max` | gauge | 3 | 0 | 1 | timeUnit (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_synonymSync_syncDurations_seconds_sum` | summary | 3 | 0 | 1 | timeUnit (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |

## mongot_system (55)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_system_cpu_count` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_cpu_info` | gauge | 3 | 0 | 1 | architecture (1), microarchitecture (1), name (1), vendor (1) | facts as labels: a table |
| `mongot_system_cpu_usage` | gauge | 3 | 3 | 3 | Scope (1) | a level that moves: a line over time; a number for now |
| `mongot_system_disk_currentQueueLength_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_disk_monitor` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_disk_readBytes_bytes` | gauge | 3 | 3 | 2 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_disk_reads_events` | gauge | 3 | 3 | 2 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_disk_space_data_path_free_bytes` | gauge | 3 | 3 | 2 |  | a level that moves: a line over time; a number for now |
| `mongot_system_disk_space_data_path_total_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_disk_space_free_bytes` | gauge | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |
| `mongot_system_disk_space_total_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_disk_transferTime_ms` | gauge | 3 | 3 | 2 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_disk_writeBytes_bytes` | gauge | 3 | 3 | 2 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_disk_writes_events` | gauge | 3 | 3 | 2 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_load_average_1m` | gauge | 3 | 3 | 2 | Scope (1) | a level that moves: a line over time; a number for now |
| `mongot_system_memory_memoryMappings_objects` | gauge | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |
| `mongot_system_memory_pageSize_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_memory_phys_available_bytes` | gauge | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |
| `mongot_system_memory_phys_inUse_bytes` | gauge | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |
| `mongot_system_memory_phys_total_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_memory_virt_inUse_bytes` | gauge | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |
| `mongot_system_memory_virt_max_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_memory_virt_swap_available_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_memory_virt_swap_inUse_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_memory_virt_swap_pagesIn_operations` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_memory_virt_swap_pagesOut_operations` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_memory_virt_swap_total_bytes` | gauge | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_active_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_completed_tasks_total` | counter | 3 | 3 | 3 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_system_metrics_updater_executor_idle_seconds_count` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_system_metrics_updater_executor_idle_seconds_max` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_idle_seconds_sum` | summary | 3 | 0 | 1 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_system_metrics_updater_executor_pool_core_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_pool_max_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_pool_size_threads` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_queue_remaining_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_queued_tasks` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_metrics_updater_executor_scheduled_once_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_system_metrics_updater_executor_scheduled_repetitively_total` | counter | 3 | 0 | 1 | name (1) | a counter: its rate over time; never the raw number |
| `mongot_system_metrics_updater_executor_seconds_count` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_system_metrics_updater_executor_seconds_max` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_metrics_updater_executor_seconds_sum` | summary | 3 | 3 | 3 | name (1) | a summary: an average from _sum over _count; its own quantiles do not combine across instances |
| `mongot_system_netstat_bytesRecv_bytes` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_netstat_bytesSent_bytes` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_netstat_collisions_events` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_netstat_inDrops_events` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_netstat_inErrors_events` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_netstat_outErrors_events` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_netstat_packetsRecv_events` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_netstat_packetsSent_events` | gauge | 3 | 3 | 3 | name (1) | a level that moves: a line over time; a number for now |
| `mongot_system_netstat_speed` | gauge | 3 | 0 | 1 | name (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_system_numa_info` | gauge | 3 | 0 | 1 | allowed_nodes (1), nodes (1), numa_balancing (1), sockets (1) | facts as labels: a table |
| `mongot_system_process_majorPageFaults_operations` | gauge | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |
| `mongot_system_process_minorPageFaults_operations` | gauge | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |
| `mongot_system_process_openFileDescriptors_objects` | gauge | 3 | 3 | 2 |  | a level that moves: a line over time; a number for now |

## mongot_vectorMergePolicy (8)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `mongot_vectorMergePolicy_budgetBytesHeapUsed` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_vectorMergePolicy_budgetBytesTotal` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_vectorMergePolicy_budgetBytesUsed` | gauge | 3 | 0 | 1 | Scope (1) | constant, the same on every series: a number or a table row, not a line |
| `mongot_vectorMergePolicy_discardedMerge_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_vectorMergePolicy_prunedSegment_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_vectorMergePolicy_segmentHeapSizeExceeded_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_vectorMergePolicy_segmentMaxSizeExceeded_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |
| `mongot_vectorMergePolicy_skippedCompoundFile_total` | counter | 3 | 0 | 1 | Scope (1) | a counter: its rate over time; never the raw number |

## scrape_body (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `scrape_body_size_bytes` | unknown | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |

## scrape_duration (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `scrape_duration_seconds` | unknown | 3 | 3 | 3 |  | a level that moves: a line over time; a number for now |

## scrape_sample (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `scrape_sample_limit` | unknown | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

## scrape_samples (2)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `scrape_samples_post_metric_relabeling` | unknown | 3 | 0 | 2 |  | constant, differing by series: a table or sorted bars, not a line |
| `scrape_samples_scraped` | unknown | 3 | 0 | 2 |  | constant, differing by series: a table or sorted bars, not a line |

## scrape_series (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `scrape_series_added` | unknown | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

## scrape_timeout (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `scrape_timeout_seconds` | unknown | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

## up (1)

| Metric | Type | Series | Changed | Distinct values | Labels | Kind of data |
| --- | --- | --- | --- | --- | --- | --- |
| `up` | unknown | 3 | 0 | 1 |  | constant, the same on every series: a number or a table row, not a line |

