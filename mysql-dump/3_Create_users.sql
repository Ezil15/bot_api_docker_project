CREATE TABLE IF NOT EXISTS `users` (
	`id` INT NOT NULL,
	`current_dialogue` INT NOT NULL DEFAULT '0'
)
COLLATE='utf8_general_ci'
;