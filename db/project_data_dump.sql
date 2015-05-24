INSERT INTO "USERS" (nickname, email, role) VALUES ('Seppo', 'seppo@jippii.fi', 'leader');
INSERT INTO "USERS" (nickname, email, role, boss) VALUES ('Teppo', 'teppo@jippii.fi', 'member', 1);
INSERT INTO "USERS" (nickname, email, role, boss) VALUES ('Reijo', 'reijo@jippii.fi', 'member', 1);
INSERT INTO "USERS" (nickname, email, role, boss) VALUES ('Kyllikki', 'kyllikki@jippii.fi', 'member', 1);
INSERT INTO "TASKS" (title, category, description, priority, status) VALUES ('Add help button', 'frontend', 'Tallanen nappi puuttuu, lisaa asap!', 2, 1);
INSERT INTO "TASKS" (title, category, description, priority, status) VALUES ('Connection bug', 'bug', 'Ei yhdistaa servulle, valittaa etta "Bad url"...', 3, 1);
INSERT INTO "ASSIGNED_TO" VALUES (1,1);
INSERT INTO "ASSIGNED_TO" VALUES (2,1);
INSERT INTO "ASSIGNED_TO" VALUES (3,1);
INSERT INTO "ASSIGNED_TO" VALUES (4,1);
INSERT INTO "COMMENTS" (comment, task_id) VALUES ('I will do this. -Teppo', 1);
INSERT INTO "COMMENTS" (comment, task_id) VALUES ('Who can start on this one??? -Seppo', 2);

