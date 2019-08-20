drop table if exists users;
 CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `cover` varchar(255) DEFAULT NULL,
  `description` longtext,
  `follows_count` varchar(255) DEFAULT NULL,
  `fans_count` varchar(255) DEFAULT NULL,
  `weibo_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


drop table if exists weibos;
 CREATE TABLE `weibos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `reposts_count` int(11) DEFAULT NULL,
  `comments_count` int(11) DEFAULT NULL,
  `attitudes_count` int(11) DEFAULT NULL,
  `text` longtext,
  `pictures` longtext,
  `source` varchar(255) DEFAULT NULL,
  `raw_text` longtext,
  `thumbnail` varchar(255) DEFAULT NULL,
  `created_at` varchar(255) DEFAULT NULL,
  `weibo_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4