CREATE TABLE IF NOT EXISTS `transitions` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`answer_id` INT NOT NULL,
    `from_dialogue` INT NOT NULL,   
	`to_dialogue` INT NOT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
;