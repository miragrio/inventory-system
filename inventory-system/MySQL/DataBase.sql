DROP TABLE `UserInventory`;
DROP TABLE `User`;
DROP TABLE `Weapon`;
DROP TABLE `Armour`;
DROP TABLE `QuestItem`;
DROP TABLE `Spell`;
DROP TABLE `HConsumable`;
DROP TABLE `MConsumable`;
DROP TABLE `ItemType`;

CREATE TABLE `User` (
`userID` INT AUTO_INCREMENT,
`username` VARCHAR(20) NOT NULL,
`health` INT,
`armour` INT,
`mana` INT,
`weight` INT,
CONSTRAINT `pri_user` PRIMARY KEY (`userID`));

CREATE TABLE `ItemType` (
`itemID` INT AUTO_INCREMENT,
`itemType` CHAR(3) NOT NULL,
`quantity` INT DEFAULT 0,
PRIMARY KEY (`itemID`));

CREATE TABLE `UserInventory` (
`userID` INT NOT NULL,
`itemID` INT NOT NULL,
`quantity` INT,
FOREIGN KEY (`userID`) REFERENCES `User` (`userID`),
FOREIGN KEY (`itemID`) REFERENCES `ItemType` (`itemID`),
PRIMARY KEY (`userID`, `itemID`));

CREATE TABLE `Weapon` (
`itemID` INT NOT NULL,
`name` VARCHAR(30) NOT NULL,
`damage` INT,
`ranged` BOOLEAN,
`weight` INT,
`note` VARCHAR(150) NULL,
FOREIGN KEY (`itemID`) REFERENCES `ItemType` (`itemID`),
PRIMARY KEY (`itemID`));

CREATE TABLE `Armour` (
`itemID` INT NOT NULL,
`name` VARCHAR(30) NOT NULL,
`armourValue` INT,
`weight` INT,
`note` VARCHAR(150) NULL,
FOREIGN KEY (`itemID`) REFERENCES `ItemType` (`itemID`),
PRIMARY KEY (`itemID`));

CREATE TABLE `QuestItem` (
`itemID` INT NOT NULL,
`name` VARCHAR(30) NOT NULL,
`weight` INT,
`note` VARCHAR(150) NULL,
FOREIGN KEY (`itemID`) REFERENCES `ItemType` (`itemID`),
PRIMARY KEY (`itemID`));

CREATE TABLE `Spell` (
`itemID` INT NOT NULL,
`name` VARCHAR(30) NOT NULL,
`damage` INT,
`manaCost` INT,
`weight` INT,
`note` VARCHAR(150) NULL,
FOREIGN KEY (`itemID`) REFERENCES `ItemType` (`itemID`),
PRIMARY KEY (`itemID`));

CREATE TABLE `HConsumable` (
`itemID` INT NOT NULL,
`name` VARCHAR(30) NOT NULL,
`healthRestore` INT,
`weight` INT,
`note` VARCHAR(150) NULL,
FOREIGN KEY (`itemID`) REFERENCES `ItemType` (`itemID`),
PRIMARY KEY (`itemID`));

CREATE TABLE `MConsumable` (
`itemID` INT NOT NULL,
`name` VARCHAR(30) NOT NULL,
`manaRegen` INT,
`weight` INT,
`note` VARCHAR(150)NULL,
FOREIGN KEY (`itemID`) REFERENCES `ItemType` (`itemID`),
PRIMARY KEY (`itemID`));