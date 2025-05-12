-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: ananda_cricket_local
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add tournament',7,'add_tournament'),(26,'Can change tournament',7,'change_tournament'),(27,'Can delete tournament',7,'delete_tournament'),(28,'Can view tournament',7,'view_tournament'),(29,'Can add player',8,'add_player'),(30,'Can change player',8,'change_player'),(31,'Can delete player',8,'delete_player'),(32,'Can view player',8,'view_player'),(33,'Can add match',9,'add_match'),(34,'Can change match',9,'change_match'),(35,'Can delete match',9,'delete_match'),(36,'Can view match',9,'view_match'),(37,'Can add substitution',10,'add_substitution'),(38,'Can change substitution',10,'change_substitution'),(39,'Can delete substitution',10,'delete_substitution'),(40,'Can view substitution',10,'view_substitution'),(41,'Can add team',11,'add_team'),(42,'Can change team',11,'change_team'),(43,'Can delete team',11,'delete_team'),(44,'Can view team',11,'view_team'),(45,'Can add team standing',12,'add_teamstanding'),(46,'Can change team standing',12,'change_teamstanding'),(47,'Can delete team standing',12,'delete_teamstanding'),(48,'Can view team standing',12,'view_teamstanding'),(49,'Can add match player',13,'add_matchplayer'),(50,'Can change match player',13,'change_matchplayer'),(51,'Can delete match player',13,'delete_matchplayer'),(52,'Can view match player',13,'view_matchplayer');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$u6bIwXMmbWghrHNiqgxnUZ$TvxtrqzSTRQ3ScPvz+SoKHwqydoXuhfxY3MIIonxAp8=','2025-05-08 15:25:31.232745',1,'admin','','','sumududias@gmail.com',1,1,'2025-05-07 11:11:25.993976'),(2,'pbkdf2_sha256$1000000$RS8KgX9d5lTebqW6DD4vlg$Ye/JaDL9Ec/i9aEzuHSbrIA6S+XKFlSx2ZvEzEcgiPE=',NULL,1,'user1','','','',1,1,'2025-05-07 11:13:36.378070');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cricket_stats_match`
--

DROP TABLE IF EXISTS `cricket_stats_match`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_stats_match` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `opponent` varchar(100) NOT NULL,
  `date` date NOT NULL,
  `venue` varchar(100) NOT NULL,
  `match_type` varchar(20) NOT NULL,
  `match_format` varchar(4) NOT NULL,
  `result` varchar(100) DEFAULT NULL,
  `ananda_extras_byes` int NOT NULL,
  `ananda_extras_leg_byes` int NOT NULL,
  `opponent_extras_byes` int NOT NULL,
  `opponent_extras_leg_byes` int NOT NULL,
  `man_of_match_id` bigint DEFAULT NULL,
  `team_id` bigint NOT NULL,
  `tournament_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cricket_stats_match_team_id_1b048170_fk_cricket_stats_team_id` (`team_id`),
  KEY `cricket_stats_match_tournament_id_4a510f82_fk_cricket_s` (`tournament_id`),
  KEY `cricket_stats_match_man_of_match_id_d3cfa97b_fk_cricket_s` (`man_of_match_id`),
  CONSTRAINT `cricket_stats_match_man_of_match_id_d3cfa97b_fk_cricket_s` FOREIGN KEY (`man_of_match_id`) REFERENCES `cricket_stats_player` (`id`),
  CONSTRAINT `cricket_stats_match_team_id_1b048170_fk_cricket_stats_team_id` FOREIGN KEY (`team_id`) REFERENCES `cricket_stats_team` (`id`),
  CONSTRAINT `cricket_stats_match_tournament_id_4a510f82_fk_cricket_s` FOREIGN KEY (`tournament_id`) REFERENCES `cricket_stats_tournament` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cricket_stats_match`
--

LOCK TABLES `cricket_stats_match` WRITE;
/*!40000 ALTER TABLE `cricket_stats_match` DISABLE KEYS */;
INSERT INTO `cricket_stats_match` VALUES (2,'Nalanda College','2025-04-02','College Home Ground','TOURNAMENT','ODI','Won',0,0,0,0,1,1,1),(3,'Royal College Colombo','2025-04-06','College Home Ground','TOURNAMENT','ODI','Won',2,5,2,8,2,1,1),(5,'PWC','2025-04-16','College Home Ground','FRIENDLY','TEST','Won',0,0,0,0,1,1,NULL),(8,'DS','2025-05-01','College Home Ground','FRIENDLY','T20','Won',0,0,0,0,1,1,NULL),(9,'DS','2025-05-03','College Home Ground','TOURNAMENT','ODI','Won',0,0,0,0,3,1,1);
/*!40000 ALTER TABLE `cricket_stats_match` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cricket_stats_matchplayer`
--

DROP TABLE IF EXISTS `cricket_stats_matchplayer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_stats_matchplayer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `innings_number` int NOT NULL,
  `batting_order` int DEFAULT NULL,
  `runs_scored` int NOT NULL,
  `balls_faced` int NOT NULL,
  `fours` int NOT NULL,
  `sixes` int NOT NULL,
  `how_out` varchar(100) NOT NULL,
  `overs_bowled` double NOT NULL,
  `runs_conceded` int NOT NULL,
  `wickets_taken` int NOT NULL,
  `wide_balls` int NOT NULL,
  `no_balls` int NOT NULL,
  `maidens` int NOT NULL,
  `catches` int NOT NULL,
  `stumpings` int NOT NULL,
  `runouts` int NOT NULL,
  `is_playing_xi` tinyint(1) NOT NULL,
  `is_substitute` tinyint(1) NOT NULL,
  `match_id` bigint NOT NULL,
  `player_id` bigint NOT NULL,
  `selection_notes` longtext,
  `approved_by` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cricket_stats_matchplaye_match_id_player_id_innin_177d2003_uniq` (`match_id`,`player_id`,`innings_number`),
  KEY `cricket_stats_matchp_player_id_e075d23c_fk_cricket_s` (`player_id`),
  CONSTRAINT `cricket_stats_matchp_match_id_564d01b5_fk_cricket_s` FOREIGN KEY (`match_id`) REFERENCES `cricket_stats_match` (`id`),
  CONSTRAINT `cricket_stats_matchp_player_id_e075d23c_fk_cricket_s` FOREIGN KEY (`player_id`) REFERENCES `cricket_stats_player` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cricket_stats_matchplayer`
--

LOCK TABLES `cricket_stats_matchplayer` WRITE;
/*!40000 ALTER TABLE `cricket_stats_matchplayer` DISABLE KEYS */;
INSERT INTO `cricket_stats_matchplayer` VALUES (1,1,1,102,88,11,4,'Cought Behind',4,20,1,1,1,1,1,0,1,1,0,2,1,NULL,NULL),(2,1,2,44,55,4,2,'LBW',0,0,0,0,0,0,2,0,0,1,0,2,2,NULL,NULL),(3,1,1,54,55,8,0,'Cought Behind',3,9,1,1,1,1,1,0,1,1,0,3,1,NULL,NULL),(4,1,2,105,99,12,3,'LBW',0,0,0,0,0,0,1,0,0,1,0,3,2,NULL,NULL),(7,1,1,71,90,8,2,'Cought Behind',12,40,1,1,1,2,1,0,1,1,0,5,1,NULL,NULL),(8,1,2,14,25,2,0,'LBW',0,0,0,0,0,0,1,0,0,1,0,5,2,NULL,NULL),(9,1,3,114,140,15,4,'LBW',0,0,0,0,0,0,0,0,0,1,0,5,8,NULL,NULL),(10,1,4,35,24,4,1,'Bowled',0,0,0,0,0,0,1,0,0,1,0,5,4,NULL,NULL),(11,1,5,48,52,5,2,'Not Out',22,88,3,1,1,2,1,0,0,1,0,5,6,NULL,NULL),(12,1,6,36,25,5,1,'Not Out',30,100,4,1,1,0,1,0,1,1,0,5,7,NULL,NULL),(13,2,1,102,88,0,0,'Bowled',20,80,5,0,0,2,1,0,1,1,0,5,5,NULL,NULL),(14,2,2,56,78,8,1,'Not Out',0,0,0,0,0,0,1,0,1,1,0,5,2,NULL,NULL),(15,2,3,77,68,10,1,'Not Out',0,0,0,0,0,0,0,0,0,1,0,5,1,NULL,NULL),(16,2,NULL,0,0,0,0,'',20,80,2,1,1,2,0,0,0,1,0,5,4,NULL,NULL),(17,2,NULL,0,0,0,0,'',15,55,1,1,1,1,0,0,0,1,0,5,7,NULL,NULL),(18,1,1,90,50,10,5,'Cought Behind',4,30,1,1,1,1,1,0,1,1,0,8,1,NULL,NULL),(19,1,2,45,35,5,1,'LBW',0,0,0,0,0,0,1,0,0,1,0,8,2,NULL,NULL),(20,1,3,5,5,1,0,'Not Out',4,40,3,1,1,0,1,0,0,1,0,8,4,NULL,NULL),(21,1,4,50,30,0,0,'Not Out',4,30,2,1,1,0,0,0,0,1,0,8,5,NULL,NULL),(22,1,NULL,0,0,0,0,'',4,35,1,1,1,0,1,0,0,1,0,8,7,NULL,NULL),(23,1,NULL,0,0,0,0,'',4,40,2,1,1,1,0,0,0,1,0,8,8,NULL,NULL),(24,1,1,56,45,5,2,'LBW',4,20,2,1,1,1,1,0,1,1,0,9,1,NULL,NULL),(28,1,1,104,96,12,4,'LBW',0,0,0,0,0,0,1,0,0,1,0,9,3,'b vnb','nvv');
/*!40000 ALTER TABLE `cricket_stats_matchplayer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cricket_stats_player`
--

DROP TABLE IF EXISTS `cricket_stats_player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_stats_player` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `dob` date NOT NULL,
  `batting_style` varchar(20) NOT NULL,
  `bowling_style` varchar(50) DEFAULT NULL,
  `primary_role` varchar(4) NOT NULL,
  `player_class` varchar(20) NOT NULL,
  `year_joined` int NOT NULL,
  `photo` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `cricket_stats_player_user_id_9306c6a8_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cricket_stats_player`
--

LOCK TABLES `cricket_stats_player` WRITE;
/*!40000 ALTER TABLE `cricket_stats_player` DISABLE KEYS */;
INSERT INTO `cricket_stats_player` VALUES (1,'Test1','Cricketer','2007-05-10','R','Right arm Spin','AR','Under-19',2023,'players/download1_-_Copy_2_sqhMmJo.jpg',1,NULL),(2,'Test2','Cricketer','2007-06-01','L','Left arm Spin','BAT','Under-19',2022,'players/download1_-_Copy_3_C3Atx0f.jpg',1,NULL),(3,'Test3','Cricketer','2007-08-02','R','Right arm Spin','BAT','Under-19',2023,'players/download1_-_Copy_4.jpg',1,NULL),(4,'Test4','Cricketer','2007-05-12','L','Left arm fast Medium','AR','Under-19',2021,'players/download1_-_Copy_5_nmsbSpp.jpg',1,NULL),(5,'Test5','Cricketer','2007-08-22','R','Right arm Spin','WK','Under-19',2021,'players/download1_-_Copy_6_6C5IVej.jpg',1,NULL),(6,'Test6','Cricketer','2007-08-20','L','Left arm Spin','AR','Under-19',2022,'players/download1_-_Copy_7_2jzKXK9.jpg',1,NULL),(7,'Test7','Cricketer','2009-01-05','L','Left arm fast Medium','AR','Under-17',2023,'players/download1_-_Copy_8_OP2DPgg.jpg',1,NULL),(8,'Test8','Cricketer','2007-05-12','L','Left arm fast Medium','BOWL','Under-19',2022,'players/download1_-_Copy_9_6ZDsgu5.jpg',1,NULL);
/*!40000 ALTER TABLE `cricket_stats_player` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cricket_stats_substitution`
--

DROP TABLE IF EXISTS `cricket_stats_substitution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_stats_substitution` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reason` varchar(20) NOT NULL,
  `comments` longtext NOT NULL,
  `substitution_time` varchar(100) NOT NULL,
  `approved_by` varchar(100) NOT NULL,
  `match_id` bigint NOT NULL,
  `player_in_id` bigint NOT NULL,
  `player_out_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cricket_stats_substituti_match_id_player_out_id_p_58631710_uniq` (`match_id`,`player_out_id`,`player_in_id`),
  KEY `cricket_stats_substi_player_in_id_47bc723c_fk_cricket_s` (`player_in_id`),
  KEY `cricket_stats_substi_player_out_id_96502694_fk_cricket_s` (`player_out_id`),
  CONSTRAINT `cricket_stats_substi_match_id_6f111c5a_fk_cricket_s` FOREIGN KEY (`match_id`) REFERENCES `cricket_stats_match` (`id`),
  CONSTRAINT `cricket_stats_substi_player_in_id_47bc723c_fk_cricket_s` FOREIGN KEY (`player_in_id`) REFERENCES `cricket_stats_player` (`id`),
  CONSTRAINT `cricket_stats_substi_player_out_id_96502694_fk_cricket_s` FOREIGN KEY (`player_out_id`) REFERENCES `cricket_stats_player` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cricket_stats_substitution`
--

LOCK TABLES `cricket_stats_substitution` WRITE;
/*!40000 ALTER TABLE `cricket_stats_substitution` DISABLE KEYS */;
INSERT INTO `cricket_stats_substitution` VALUES (1,'TACTICAL','test','whole match','Coach',5,8,3),(2,'INJURY','nb','5th over to 20 over','',9,5,1);
/*!40000 ALTER TABLE `cricket_stats_substitution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cricket_stats_team`
--

DROP TABLE IF EXISTS `cricket_stats_team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_stats_team` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `season` varchar(20) NOT NULL,
  `coach` varchar(100) NOT NULL,
  `captain_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cricket_stats_team_captain_id_a444f141_fk_cricket_s` (`captain_id`),
  CONSTRAINT `cricket_stats_team_captain_id_a444f141_fk_cricket_s` FOREIGN KEY (`captain_id`) REFERENCES `cricket_stats_player` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cricket_stats_team`
--

LOCK TABLES `cricket_stats_team` WRITE;
/*!40000 ALTER TABLE `cricket_stats_team` DISABLE KEYS */;
INSERT INTO `cricket_stats_team` VALUES (1,'First Xi','2025','coach1',1),(2,'Under-17','2025','coach1',7);
/*!40000 ALTER TABLE `cricket_stats_team` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cricket_stats_teamstanding`
--

DROP TABLE IF EXISTS `cricket_stats_teamstanding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_stats_teamstanding` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `matches_played` int NOT NULL,
  `matches_won` int NOT NULL,
  `matches_lost` int NOT NULL,
  `matches_drawn` int NOT NULL,
  `points` int NOT NULL,
  `net_run_rate` double NOT NULL,
  `position` int NOT NULL,
  `team_id` bigint NOT NULL,
  `tournament_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cricket_stats_teamst_team_id_ab6914ec_fk_cricket_s` (`team_id`),
  KEY `cricket_stats_teamst_tournament_id_9e5a3fa0_fk_cricket_s` (`tournament_id`),
  CONSTRAINT `cricket_stats_teamst_team_id_ab6914ec_fk_cricket_s` FOREIGN KEY (`team_id`) REFERENCES `cricket_stats_team` (`id`),
  CONSTRAINT `cricket_stats_teamst_tournament_id_9e5a3fa0_fk_cricket_s` FOREIGN KEY (`tournament_id`) REFERENCES `cricket_stats_tournament` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cricket_stats_teamstanding`
--

LOCK TABLES `cricket_stats_teamstanding` WRITE;
/*!40000 ALTER TABLE `cricket_stats_teamstanding` DISABLE KEYS */;
/*!40000 ALTER TABLE `cricket_stats_teamstanding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cricket_stats_tournament`
--

DROP TABLE IF EXISTS `cricket_stats_tournament`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_stats_tournament` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `season` varchar(20) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `organizer` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cricket_stats_tournament`
--

LOCK TABLES `cricket_stats_tournament` WRITE;
/*!40000 ALTER TABLE `cricket_stats_tournament` DISABLE KEYS */;
INSERT INTO `cricket_stats_tournament` VALUES (1,'2025 All Island','2025','2025-04-01','2025-05-30','SLCB');
/*!40000 ALTER TABLE `cricket_stats_tournament` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-05-08 17:20:08.520190','1','2025 All Island 2025',1,'[{\"added\": {}}]',7,1),(2,'2025-05-08 17:58:28.666816','1','Test1 Cricketer',1,'[{\"added\": {}}]',8,1),(3,'2025-05-08 17:59:11.353844','2','Test2 Cricketer',1,'[{\"added\": {}}]',8,1),(4,'2025-05-08 18:00:26.981825','3','Test3 Cricketer',1,'[{\"added\": {}}]',8,1),(5,'2025-05-08 18:01:14.262562','4','Test4 Cricketer',1,'[{\"added\": {}}]',8,1),(6,'2025-05-08 18:02:53.456821','5','Test5 Cricketer',1,'[{\"added\": {}}]',8,1),(7,'2025-05-08 18:04:39.467977','6','Test6 Cricketer',1,'[{\"added\": {}}]',8,1),(8,'2025-05-08 18:06:07.109368','7','Test7 Cricketer',1,'[{\"added\": {}}]',8,1),(9,'2025-05-08 18:13:59.002143','1','First Xi (2025)',1,'[{\"added\": {}}]',11,1),(10,'2025-05-08 18:15:07.389543','2','Under-17 (2025)',1,'[{\"added\": {}}]',11,1),(11,'2025-05-08 20:40:16.756649','1','First Xi (2025)',2,'[]',11,1),(12,'2025-05-08 20:46:12.887391','2','One Day (50 Overs) vs Nalanda College on 2025-04-02',1,'[{\"added\": {}}, {\"added\": {\"name\": \"match player\", \"object\": \"MatchPlayer object (1)\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"MatchPlayer object (2)\"}}]',9,1),(13,'2025-05-08 20:52:26.916801','3','One Day (50 Overs) vs Royal College Colombo on 2025-04-06',1,'[{\"added\": {}}, {\"added\": {\"name\": \"match player\", \"object\": \"MatchPlayer object (3)\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"MatchPlayer object (4)\"}}]',9,1),(14,'2025-05-10 04:40:34.978255','4','Test Match vs Nalanda College on 2025-04-16',1,'[{\"added\": {}}]',9,1),(15,'2025-05-10 04:41:15.465831','4','Test Match vs Nalanda College on 2025-04-16',3,'',9,1),(16,'2025-05-10 04:43:11.176898','5','Test Match vs Royal College Colombo on 2025-04-16',1,'[{\"added\": {}}]',9,1),(17,'2025-05-10 06:56:54.363284','6','Test Match vs xxxx on 2025-04-02',1,'[{\"added\": {}}]',9,1),(18,'2025-05-10 07:30:49.691279','6','Test Match vs xxxx on 2025-04-02',2,'[]',9,1),(19,'2025-05-10 07:44:19.260650','7','Test Match vs PWC on 2025-04-25',1,'[{\"added\": {}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test1 Cricketer - Test Match vs PWC on 2025-04-25 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test2 Cricketer - Test Match vs PWC on 2025-04-25 - Innings 1\"}}]',9,1),(20,'2025-05-10 07:57:29.230455','7','Test Match vs PWC on 2025-04-25',3,'',9,1),(21,'2025-05-10 07:57:29.230455','6','Test Match vs xxxx on 2025-04-02',3,'',9,1),(22,'2025-05-10 08:20:31.785440','1','Test3 Cricketer → Test6 Cricketer in Test Match vs Royal College Colombo on 2025-04-16',1,'[{\"added\": {}}]',10,1),(23,'2025-05-10 09:27:17.863774','5','Test Match vs PWC on 2025-04-16',2,'[{\"changed\": {\"fields\": [\"Opponent\", \"Result\", \"Man of match\"]}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test1 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test2 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test3 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test4 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\"}}]',9,1),(24,'2025-05-10 09:45:01.253877','5','Test Match vs PWC on 2025-04-16',2,'[{\"added\": {\"name\": \"match player\", \"object\": \"Test6 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test7 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test1 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test2 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test3 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test6 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test7 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\"}}, {\"changed\": {\"name\": \"match player\", \"object\": \"Test4 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\", \"fields\": [\"How out\"]}}]',9,1),(25,'2025-05-10 17:00:40.971882','8','Test8 Cricketer',1,'[{\"added\": {}}]',8,1),(26,'2025-05-10 17:01:41.869514','5','Test Match vs PWC on 2025-04-16',2,'[{\"changed\": {\"name\": \"match player\", \"object\": \"Test4 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\", \"fields\": [\"Player\"]}}, {\"changed\": {\"name\": \"match player\", \"object\": \"Test5 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\", \"fields\": [\"Player\"]}}, {\"changed\": {\"name\": \"substitution\", \"object\": \"Test3 Cricketer \\u2192 Test8 Cricketer (Tactical)\", \"fields\": [\"Player in\"]}}]',9,1),(27,'2025-05-10 17:02:44.814906','5','Test Match vs PWC on 2025-04-16',2,'[{\"changed\": {\"name\": \"match player\", \"object\": \"Test1 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 2\", \"fields\": [\"Player\"]}}]',9,1),(28,'2025-05-10 17:05:39.322067','5','Test Match vs PWC on 2025-04-16',2,'[{\"changed\": {\"name\": \"match player\", \"object\": \"Test8 Cricketer - Test Match vs PWC on 2025-04-16 - Innings 1\", \"fields\": [\"Player\"]}}]',9,1),(29,'2025-05-10 18:38:13.132734','8','Twenty20 vs DS on 2025-05-01',1,'[{\"added\": {}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test1 Cricketer - Twenty20 vs DS on 2025-05-01 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test2 Cricketer - Twenty20 vs DS on 2025-05-01 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test4 Cricketer - Twenty20 vs DS on 2025-05-01 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test5 Cricketer - Twenty20 vs DS on 2025-05-01 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test7 Cricketer - Twenty20 vs DS on 2025-05-01 - Innings 1\"}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test8 Cricketer - Twenty20 vs DS on 2025-05-01 - Innings 1\"}}]',9,1),(30,'2025-05-10 18:41:54.152431','9','One Day 50 Over Match vs DS on 2025-05-03',1,'[{\"added\": {}}, {\"added\": {\"name\": \"match player\", \"object\": \"Test1 Cricketer - One Day 50 Over Match vs DS on 2025-05-03 - Innings 1\"}}]',9,1),(31,'2025-05-10 23:03:46.794505','9','One Day 50 Over Match vs DS on 2025-05-03',2,'[{\"added\": {\"name\": \"match player\", \"object\": \"Test3 Cricketer - One Day 50 Over Match vs DS on 2025-05-03 - Innings 1\"}}, {\"added\": {\"name\": \"substitution\", \"object\": \"Test1 Cricketer replaced by Test5 Cricketer in One Day 50 Over Match vs DS on 2025-05-03\"}}]',9,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(9,'cricket_stats','match'),(13,'cricket_stats','matchplayer'),(8,'cricket_stats','player'),(10,'cricket_stats','substitution'),(11,'cricket_stats','team'),(12,'cricket_stats','teamstanding'),(7,'cricket_stats','tournament'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-05-07 11:09:04.382822'),(2,'auth','0001_initial','2025-05-07 11:09:05.841113'),(3,'admin','0001_initial','2025-05-07 11:09:06.183867'),(4,'admin','0002_logentry_remove_auto_add','2025-05-07 11:09:06.199582'),(5,'admin','0003_logentry_add_action_flag_choices','2025-05-07 11:09:06.203091'),(6,'contenttypes','0002_remove_content_type_name','2025-05-07 11:09:06.434220'),(7,'auth','0002_alter_permission_name_max_length','2025-05-07 11:09:06.578952'),(8,'auth','0003_alter_user_email_max_length','2025-05-07 11:09:06.610885'),(9,'auth','0004_alter_user_username_opts','2025-05-07 11:09:06.626477'),(10,'auth','0005_alter_user_last_login_null','2025-05-07 11:09:06.753088'),(11,'auth','0006_require_contenttypes_0002','2025-05-07 11:09:06.766979'),(12,'auth','0007_alter_validators_add_error_messages','2025-05-07 11:09:06.766979'),(13,'auth','0008_alter_user_username_max_length','2025-05-07 11:09:06.910343'),(14,'auth','0009_alter_user_last_name_max_length','2025-05-07 11:09:07.070532'),(15,'auth','0010_alter_group_name_max_length','2025-05-07 11:09:07.102862'),(16,'auth','0011_update_proxy_permissions','2025-05-07 11:09:07.102862'),(17,'auth','0012_alter_user_first_name_max_length','2025-05-07 11:09:07.253228'),(18,'cricket_stats','0001_initial','2025-05-07 11:09:09.329824'),(19,'sessions','0001_initial','2025-05-07 11:09:09.410810'),(20,'cricket_stats','0002_alter_match_result','2025-05-08 21:12:39.398733'),(21,'cricket_stats','0003_update_matchplayer','2025-05-10 03:03:56.733581'),(22,'cricket_stats','0002_add_selection_notes','2025-05-10 21:55:56.748478'),(23,'cricket_stats','0004_merge_20250511_0325','2025-05-10 21:55:56.762769'),(24,'cricket_stats','0005_update_matchplayer_fields','2025-05-10 22:12:51.867300'),(25,'cricket_stats','0006_alter_substitution_options_and_more','2025-05-10 22:12:53.824340'),(26,'cricket_stats','0006_update_substitution_model','2025-05-10 22:58:49.225812');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('hsv4fkvoo8f9247hk8b0swt0hasvuq5s','.eJxVjEEOwiAQRe_C2pAOBTq4dO8ZyMAMUjVtUtqV8e7apAvd_vfef6lI21rj1mSJI6uzAnX63RLlh0w74DtNt1nneVqXMeld0Qdt-jqzPC-H-3dQqdVvnUowPvc8DCwmgHEABtFZC9SJoHcd2iCFkDMJZQh9b3yBJBIQ2aB6fwDTlje2:1uD37r:-T1SuGU6A43HNIdpPLoFZIxIEkMA4Zdyu0Yb63kMDMg','2025-05-22 15:25:31.235132');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-11  6:20:34
