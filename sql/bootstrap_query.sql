DROP DATABASE IF EXISTS surer;

CREATE DATABASE surer;
USE surer;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
    `email` VARCHAR(256) NOT NULL,
    `hashed_password` VARCHAR(256),
    `salt` VARCHAR(256),
    `first_name` VARCHAR(256) NOT NULL,
    `last_name` VARCHAR(256) NOT NULL,
    PRIMARY KEY (`email`)
);

DROP TABLE IF EXISTS `project`;
CREATE TABLE `project` (
    `project_id` INT AUTO_INCREMENT NOT NULL,
    `creator` VARCHAR(256) NOT NULL,
    `description` VARCHAR(1000) NOT NULL,
    `created_at` DATE NOT NULL,
    `last_modified` DATE NOT NULL,

    PRIMARY KEY (`project_id`)
);

DROP TABLE IF EXISTS `team`;
CREATE TABLE `team` (
    `user_email` VARCHAR(256) NOT NULL,
    `project_id` INT NOT NULL,

    PRIMARY KEY (`user_email`, `project_id`),
    FOREIGN KEY (`user_email`) REFERENCES `user` (`email`),
    FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`)
);

DROP TABLE IF EXISTS `task`;
CREATE TABLE `task` (
    `task_id` INT AUTO_INCREMENT NOT NULL,
    `project_id` INT NOT NULL,
    `title` VARCHAR(1000) NOT NULL,
    `description` VARCHAR(1000),
    `position` INT NOT NULL,
    `created_datetime` TIMESTAMP NOT NULL,
    `deadline` TIMESTAMP,
    `completion_status` VARCHAR(256) NOT NULL,

    PRIMARY KEY (`task_id`),
    FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`)
);

DROP TABLE IF EXISTS `assignee`;
CREATE TABLE `assignee` (
    `task_id` INT NOT NULL,
    `project_id` INT NOT NULL,
    `user_email` VARCHAR(256) NOT NULL,
    `fname` VARCHAR(256) NOT NULL,
    `lname` VARCHAR(256) NOT NULL,


    PRIMARY KEY (`task_id`, `project_id`, `user_email`),
    FOREIGN KEY (`user_email`) REFERENCES `user` (`email`),
    FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`),
    FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`)
);


-- import users
INSERT INTO user (email, hashed_password, salt, first_name, last_name)
VALUES ('admin@admin.com', 'fa6a2185b3e0a9a85ef41ffb67ef3c1fb6f74980f8ebf970e4e72e353ed9537d593083c201dfd6e43e1c8a7aac2bc8dbb119c7dfb7d4b8f131111395bd70e97f', 'salt', 'Admin', 'Istrator'),
    ('john@gmail.com', 'fa6a2185b3e0a9a85ef41ffb67ef3c1fb6f74980f8ebf970e4e72e353ed9537d593083c201dfd6e43e1c8a7aac2bc8dbb119c7dfb7d4b8f131111395bd70e97f', 'salt', 'John', 'Cena'),
    ('mark@hotmail.com', 'fa6a2185b3e0a9a85ef41ffb67ef3c1fb6f74980f8ebf970e4e72e353ed9537d593083c201dfd6e43e1c8a7aac2bc8dbb119c7dfb7d4b8f131111395bd70e97f', 'salt', 'Marks', 'Spencer'),
    ('larry@hotmail.com', 'fa6a2185b3e0a9a85ef41ffb67ef3c1fb6f74980f8ebf970e4e72e353ed9537d593083c201dfd6e43e1c8a7aac2bc8dbb119c7dfb7d4b8f131111395bd70e97f', 'salt', 'Larry', 'Bird');
-- import project

INSERT INTO project (project_id, creator, description, created_at, last_modified)
VALUES (1,'admin@admin.com','WAD2','2022-02-15 21:00:14', '2022-02-16 21:00:14'),
	(2,'john@gmail.com','NLC','2022-02-16 21:00:14', '2022-02-17 21:00:14'),
	(3,'mark@hotmail.com','SPM','2022-02-17 21:00:14', '2022-02-18 21:00:14'),
	(4,'larry@hotmail.com','BPAS','2022-02-18 21:00:14', '2022-02-19 21:00:14');


-- import sessions
CREATE TABLE `sessions` (
    `user_email` VARCHAR(256) NOT NULL,
    `session_id` VARCHAR(256) NOT NULL,

    PRIMARY KEY (`user_email`, `session_id`),
    FOREIGN KEY (`user_email`) REFERENCES `user` (`email`)
);
