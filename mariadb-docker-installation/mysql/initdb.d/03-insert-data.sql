USE test-db1;

INSERT INTO `User1`
(userId, roleCode, roleGroup)
VALUES(1, 'ADMIN', 'role');

USE test-db2;
INSERT INTO `User2`
(userId, roleCode, roleGroup)
VALUES(1, 'ADMIN', 'role');
