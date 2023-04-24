CREATE TABLE IF NOT EXISTS admission (student_id INTEGER PRIMARY KEY) WITH (KAFKA_TOPIC='ADMISSION_SRC_REKEY',VALUE_FORMAT='AVRO');

CREATE TABLE IF NOT EXISTS research (student_id INTEGER PRIMARY KEY) WITH (KAFKA_TOPIC='RESEARCH_SRC_REKEY',VALUE_FORMAT='AVRO');

-- JOIN
CREATE TABLE IF NOT EXISTS research_boost 
 WITH (KAFKA_TOPIC='RESEARCH_BOOST', VALUE_FORMAT='AVRO') 
 AS SELECT a.student_id as student_id, 
 a.admit_chance as admit_chance, 
 r.research as research 
 FROM admission a 
 LEFT JOIN research r on a.student_id = r.student_id;


-- GROUP & COMPUTE
CREATE TABLE IF NOT EXISTS research_ave_boost 
 WITH (KAFKA_TOPIC='RESEARCH_AVE_BOOST', VALUE_FORMAT='AVRO') 
 AS SELECT research, SUM(admit_chance)/COUNT(admit_chance) as ave_chance 
 FROM research_boost 
 GROUP BY research;

