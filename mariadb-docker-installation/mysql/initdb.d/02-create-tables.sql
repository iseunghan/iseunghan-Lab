-- 첫 번쩨 DB의 테이블 생성
USE `test-db1`;

CREATE TABLE `User1` (
  `userId` bigint(20) unsigned NOT NULL,
	...
  PRIMARY KEY (`userId`),
  UNIQUE KEY `UK_1moq4ur264iwsfkldd425o04y` (`userId`),
  KEY `IDX1moq4ur264iwsfkldd425o04y` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;


-- 두 번쩨 DB의 테이블 생성
USE `test-db2`;

CREATE TABLE `User1` (
  `userId` bigint(20) unsigned NOT NULL,
	...
  PRIMARY KEY (`userId`),
  UNIQUE KEY `UK_1moq4ur264iwsfkldd425o04y` (`userId`),
  KEY `IDX1moq4ur264iwsfkldd425o04y` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
