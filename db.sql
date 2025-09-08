-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: retrospective
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `decision_assignments`
--

DROP TABLE IF EXISTS `decision_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `decision_assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `decision_id` int NOT NULL,
  `executor_id` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_decision` (`decision_id`),
  KEY `executor_id` (`executor_id`),
  CONSTRAINT `decision_assignments_ibfk_1` FOREIGN KEY (`decision_id`) REFERENCES `idea_decision` (`id_idea_decision`) ON DELETE CASCADE,
  CONSTRAINT `decision_assignments_ibfk_2` FOREIGN KEY (`executor_id`) REFERENCES `user` (`id_user`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decision_assignments`
--

LOCK TABLES `decision_assignments` WRITE;
/*!40000 ALTER TABLE `decision_assignments` DISABLE KEYS */;
/*!40000 ALTER TABLE `decision_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `idea`
--

DROP TABLE IF EXISTS `idea`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `idea` (
  `id_idea` int NOT NULL AUTO_INCREMENT,
  `type_idea_id_type_idea` int NOT NULL,
  `user_id_user` int NOT NULL,
  `name` varchar(45) NOT NULL,
  `description` varchar(200) NOT NULL,
  `vote` int DEFAULT NULL,
  PRIMARY KEY (`id_idea`,`type_idea_id_type_idea`,`user_id_user`),
  KEY `fk_idea_user1_idx` (`user_id_user`),
  KEY `fk_idea_type_idea1_idx` (`type_idea_id_type_idea`),
  CONSTRAINT `fk_idea_type_idea1` FOREIGN KEY (`type_idea_id_type_idea`) REFERENCES `type_idea` (`id_type_idea`),
  CONSTRAINT `fk_idea_user1` FOREIGN KEY (`user_id_user`) REFERENCES `user` (`id_user`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=247 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `idea`
--

LOCK TABLES `idea` WRITE;
/*!40000 ALTER TABLE `idea` DISABLE KEYS */;
/*!40000 ALTER TABLE `idea` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `idea_decision`
--

DROP TABLE IF EXISTS `idea_decision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `idea_decision` (
  `id_idea_decision` int NOT NULL AUTO_INCREMENT,
  `idea_id_idea` int NOT NULL,
  `user_id_user` int NOT NULL,
  `name` varchar(45) NOT NULL,
  `description` varchar(200) NOT NULL,
  `vote` int DEFAULT NULL,
  PRIMARY KEY (`id_idea_decision`,`idea_id_idea`,`user_id_user`),
  KEY `fk_idea_decision_idea1_idx` (`idea_id_idea`),
  KEY `fk_idea_decision_user1_idx` (`user_id_user`),
  CONSTRAINT `fk_idea_decision_idea1` FOREIGN KEY (`idea_id_idea`) REFERENCES `idea` (`id_idea`) ON DELETE CASCADE,
  CONSTRAINT `fk_idea_decision_user1` FOREIGN KEY (`user_id_user`) REFERENCES `user` (`id_user`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `idea_decision`
--

LOCK TABLES `idea_decision` WRITE;
/*!40000 ALTER TABLE `idea_decision` DISABLE KEYS */;
/*!40000 ALTER TABLE `idea_decision` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `retrospective_topic`
--

DROP TABLE IF EXISTS `retrospective_topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `retrospective_topic` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `retrospective_topic`
--

LOCK TABLES `retrospective_topic` WRITE;
/*!40000 ALTER TABLE `retrospective_topic` DISABLE KEYS */;
INSERT INTO `retrospective_topic` VALUES (1,'');
/*!40000 ALTER TABLE `retrospective_topic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_state`
--

DROP TABLE IF EXISTS `session_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session_state` (
  `id` int NOT NULL AUTO_INCREMENT,
  `is_active` tinyint(1) NOT NULL DEFAULT '0',
  `voting_active` tinyint(1) NOT NULL DEFAULT '0',
  `collecting_decisions` tinyint(1) DEFAULT '0',
  `voting_decision_active` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_state`
--

LOCK TABLES `session_state` WRITE;
/*!40000 ALTER TABLE `session_state` DISABLE KEYS */;
INSERT INTO `session_state` VALUES (1,0,0,0,0);
/*!40000 ALTER TABLE `session_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `type_account`
--

DROP TABLE IF EXISTS `type_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `type_account` (
  `id_type_account` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id_type_account`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `type_account`
--

LOCK TABLES `type_account` WRITE;
/*!40000 ALTER TABLE `type_account` DISABLE KEYS */;
INSERT INTO `type_account` VALUES (1,'Администратор'),(2,'Фасилитатор'),(3,'Участник');
/*!40000 ALTER TABLE `type_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `type_idea`
--

DROP TABLE IF EXISTS `type_idea`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `type_idea` (
  `id_type_idea` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id_type_idea`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `type_idea`
--

LOCK TABLES `type_idea` WRITE;
/*!40000 ALTER TABLE `type_idea` DISABLE KEYS */;
INSERT INTO `type_idea` VALUES (1,'Что прошло хорошо'),(2,'Что прошло плохо');
/*!40000 ALTER TABLE `type_idea` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id_user` int NOT NULL AUTO_INCREMENT,
  `type_account_id_type_account` int NOT NULL,
  `name` varchar(45) NOT NULL,
  `password` varchar(64) NOT NULL,
  PRIMARY KEY (`id_user`,`type_account_id_type_account`),
  KEY `fk_user_type_account_idx` (`type_account_id_type_account`),
  CONSTRAINT `fk_user_type_account` FOREIGN KEY (`type_account_id_type_account`) REFERENCES `type_account` (`id_type_account`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (5,1,'root','4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `votes_cast`
--

DROP TABLE IF EXISTS `votes_cast`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `votes_cast` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `voted_stage1` tinyint(1) DEFAULT '0',
  `voted_stage2` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `votes_cast_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id_user`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `votes_cast`
--

LOCK TABLES `votes_cast` WRITE;
/*!40000 ALTER TABLE `votes_cast` DISABLE KEYS */;
/*!40000 ALTER TABLE `votes_cast` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-06 19:46:41
