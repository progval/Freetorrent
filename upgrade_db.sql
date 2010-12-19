RENAME TABLE `freetorrent`.`namemap`  TO `freetorrent`.`torrents` ;

ALTER TABLE `torrents`
  DROP `info`,
  DROP `lastupdate`,
  DROP `external`,
  DROP `anonymous`,
  DROP `lastsuccess`,
  DROP `torr_passw`,
  DROP `sub_url`;

ALTER TABLE `torrents` CHANGE `filename` `name` VARCHAR( 250 ) 
CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '';

ALTER TABLE `torrents` CHANGE `url` `local_filename` VARCHAR( 250 )
CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '';

ALTER TABLE `torrents` CHANGE `torr_url` `url` VARCHAR( 500 )
CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL;

ALTER TABLE `torrents` CHANGE `data` `submit_time` DATETIME NOT NULL
DEFAULT '0000-00-00 00:00:00';

ALTER TABLE `torrents` CHANGE `info_hash` `t_id` VARCHAR( 40 )
CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '';

ALTER TABLE `torrents` CHANGE `category` `c_id` INT( 10 ) UNSIGNED NOT NULL
DEFAULT '0';

ALTER TABLE `torrents` CHANGE `comment` `description` TEXT
CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL;
