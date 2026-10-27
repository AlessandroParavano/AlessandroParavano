// My degree as a Neo4j graph. Paste into Neo4j Browser (or `cypher-shell < modules.cypher`).
// Source: University of Pretoria 2026 yearbook.  Regenerate with: python3 scripts/make_graph.py

CREATE (:Module {code: 'COS110', name: 'Program design: Introduction', year: 2024, status: 'passed'});
CREATE (:Module {code: 'COS122', name: 'Operating systems', year: 2024, status: 'passed'});
CREATE (:Module {code: 'COS132', name: 'Imperative programming', year: 2024, status: 'distinction', mark: 76});
CREATE (:Module {code: 'COS151', name: 'Introduction to computer science', year: 2024, status: 'passed'});
CREATE (:Module {code: 'COS210', name: 'Theoretical computer science', year: 2025, status: 'distinction', mark: 87});
CREATE (:Module {code: 'COS212', name: 'Data structures and algorithms', year: 2025, status: 'distinction', mark: 84});
CREATE (:Module {code: 'COS214', name: 'Software modelling', year: 2025, status: 'passed'});
CREATE (:Module {code: 'COS216', name: 'Netcentric computer systems', year: 2025, status: 'distinction', mark: 84});
CREATE (:Module {code: 'COS221', name: 'Introduction to database systems', year: 2025, status: 'distinction', mark: 75});
CREATE (:Module {code: 'COS226', name: 'Concurrent systems', year: 2025, status: 'distinction', mark: 76});
CREATE (:Module {code: 'COS284', name: 'Computer organisation and architecture', year: 2025, status: 'distinction', mark: 85});
CREATE (:Module {code: 'COS301', name: 'Software engineering', year: 2026, status: 'in-progress'});
CREATE (:Module {code: 'COS314', name: 'Artificial intelligence', year: 2026, status: 'distinction', mark: 75});
CREATE (:Module {code: 'COS326', name: 'Database systems', year: 2026, status: 'in-progress'});
CREATE (:Module {code: 'COS330', name: 'Computer security and ethics', year: 2026, status: 'in-progress'});
CREATE (:Module {code: 'COS332', name: 'Computer networks', year: 2026, status: 'passed'});
CREATE (:Module {code: 'COS333', name: 'Programming languages', year: 2026, status: 'distinction', mark: 76});
CREATE (:Module {code: 'COS341', name: 'Compiler construction', year: 2026, status: 'in-progress'});
CREATE (:Module {code: 'COS344', name: 'Computer graphics', year: 2026, status: 'distinction', mark: 90});
CREATE (:Module {code: 'WTW146', name: 'Linear algebra', year: 2024, status: 'passed'});

MATCH (a:Module {code: 'COS132'}), (b:Module {code: 'COS110'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS151'}), (b:Module {code: 'COS110'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS132'}), (b:Module {code: 'COS122'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS210'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS151'}), (b:Module {code: 'COS210'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS212'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS212'}), (b:Module {code: 'COS214'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS216'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS221'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS122'}), (b:Module {code: 'COS226'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS212'}), (b:Module {code: 'COS226'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS212'}), (b:Module {code: 'COS284'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS212'}), (b:Module {code: 'COS301'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS214'}), (b:Module {code: 'COS301'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS314'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS221'}), (b:Module {code: 'COS326'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS330'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS216'}), (b:Module {code: 'COS332'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS333'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS210'}), (b:Module {code: 'COS341'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS212'}), (b:Module {code: 'COS341'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'COS110'}), (b:Module {code: 'COS344'}) CREATE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Module {code: 'WTW146'}), (b:Module {code: 'COS344'}) CREATE (a)-[:PREREQUISITE_OF]->(b);

// The long way to the capstone:
// MATCH path = (:Module {code: 'COS110'})-[:PREREQUISITE_OF*]->(:Module {code: 'COS301'}) RETURN path;

// The most connected module (spoiler: COS 110, with eight dependants):
// MATCH (m:Module)-[r:PREREQUISITE_OF]->() RETURN m.code, count(r) AS unlocks ORDER BY unlocks DESC LIMIT 3;
