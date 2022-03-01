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
    `details` VARCHAR(1000) NOT NULL,    
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
INSERT INTO project (project_id, creator, description, details, created_at, last_modified)
VALUES (1,'admin@admin.com','WAD2','Web Application Developement 2, where we learn about the HTML, CSS, JS, and VueJS','2022-02-15 21:00:14', '2022-02-16 21:00:14'),
	(2,'john@gmail.com','SMA','Spreadsheet Modelling & Analysis. Where we learn about the various functions of excel and how to use it efficiently','2022-02-16 21:00:14', '2022-02-17 21:00:14'),
	(3,'mark@hotmail.com','SPM','Software Project Management. Agile Methods to build software','2022-02-17 21:00:14', '2022-02-18 21:00:14'),
	(4,'larry@hotmail.com','BPAS','Business workflow and recommend solutions based on technology solutioning or restructuring workflows for process optimization','2022-02-18 21:00:14', '2022-02-19 21:00:14');
    
-- import team
INSERT INTO team (user_email, project_id)
VALUES ('admin@admin.com', 1),
	('admin@admin.com', 2),
    ('admin@admin.com', 3),
    ('larry@hotmail.com', 1),
    ('larry@hotmail.com', 2),
	('larry@hotmail.com', 4),
    ('john@gmail.com', 1),
	('john@gmail.com', 3),
    ('mark@hotmail.com', 1),    
    ('mark@hotmail.com', 3);

-- import task
INSERT INTO task (task_id, project_id, title,description, position, created_datetime, deadline, completion_status)
VALUES (1, 1, 'Front end','Create vue template', 0, '2022-02-18 21:00:14','2022-02-18', 'started'),
    (2, 1, 'Back end','Set up flask application', 0,'2022-02-18 21:00:14','2022-02-18', 'not started'),
    (3, 2, 'Fine tune BERT','Explore different fine-tuning methods', 0, '2022-02-18 21:00:14','2022-02-18', 'started'),
    (4, 2, 'Look at research paper','literature review', 0, '2022-02-18 21:00:14','2022-02-18', 'not started');

-- import assignee
INSERT INTO assignee (task_id, project_id, user_email, fname, lname)
VALUES (1, 1, 'admin@admin.com', 'Admin', 'Istrator'),
(2,1,'admin@admin.com', 'Admin', 'Istrator'),
(2,1, 'larry@hotmail.com', 'Larry', 'Bird'),
(3,2,'admin@admin.com', 'Admin', 'Istrator'),
(4,2,'admin@admin.com', 'Admin', 'Istrator');

-- import sessions
CREATE TABLE `sessions` (
    `user_email` VARCHAR(256) NOT NULL,
    `session_id` VARCHAR(256) NOT NULL,

    PRIMARY KEY (`user_email`, `session_id`),
    FOREIGN KEY (`user_email`) REFERENCES `user` (`email`)
);
