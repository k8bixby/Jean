with s as (
    select 
    q.date
    , q.name
    , n.original_capture_name
    , n.event_name
    , COALESCE(SUM(q.scans),0) as total_scans
    from dev.qr_code_table q
    left join dev.aggregate_table n 
    on n.event_name=q.name 
    and n.date=q.date 
    where q.date > '2021-12-31' 
    group by 
    q.date
    , q.name
    , n.event_name
    , n.original_capture_name),

a as (
    select 
    e.name
    , z.date
    , max(z.zone_uuid) as zone_uuid 
    , z.date
    , z.zone_uuid
    , z.passerby_visitors
    , z.total_visitors
    , z.engaged_visitors 
    from dev.event_data_zones z
    left join dev.event_data e 
    on z.event_uuid = e.event_uuid 
    group by 
    e.name
    , z.date)


select 
s.date
, s.name
, s.event_name
, s.original_capture_name
, s.total_scans
, l.site_visits
, l.metric_1
, l.metric_2
, l.attendance
, l.impressions
, l.premiums
, a.engaged_visitors as engaged_audience
, a.passerby_visitors+a.engaged_visitors as area_of_influence 
from s
left join dev.lqa_master l 
on s.name=l.name 
and s.date=l.date 
left join a 
on a.date=s.date 
and n.original_capture_name = a.name


