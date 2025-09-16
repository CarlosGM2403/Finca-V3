-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 16-09-2025 a las 16:26:18
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `flask_login`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` smallint(3) UNSIGNED NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` char(202) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `fullname` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `must_change_password` tinyint(1) DEFAULT 1,
  `rol` enum('administrador','supervisor','empleado','cuidador') NOT NULL DEFAULT 'empleado',
  `estado` enum('habilitado','inhabilitado') DEFAULT 'habilitado',
  `fecha_registro` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `user`
--

INSERT INTO `user` (`id`, `username`, `password`, `fullname`, `must_change_password`, `rol`, `estado`, `fecha_registro`) VALUES
(36, 'estebangallego757@gmail.com', 'scrypt:32768:8:1$s1DVKj7ZCtJfAK4n$9213bcf248df2ad6ecc4f104055a76cc34aa1e7f1d38d99aac364a69a9b16bb2c1244d173e381fd527f4e8a78057b2737dbc2d8ad29524ce075a508288b43006', 'David', 0, 'administrador', 'habilitado', '2025-09-11 19:23:55'),
(37, 'garciamcarlos2403@gmail.com', 'scrypt:32768:8:1$OuPR6L2cRYPqcJvc$959f5ae332614703a91b592420c1ae60ebc646662f114c7bfb57b420eeabe5a9852223eac88cfb0f625f412f48632de220fae40c511eb27193f4bdbdc25b589d', 'Carlos Garcia', 0, 'empleado', 'habilitado', '2025-09-11 19:24:21'),
(40, 'carolinamelendez860@gmail.com', 'scrypt:32768:8:1$1qn6s8V8nzOBm8W6$31a4dd2d1fad2cd09b3021f880f876740df9f9a0e4011aa66075a7ac9aef3cebb2f821a163c05aa21a9c1bef26122bbac5608119b16650b9caee47833f08a3f0', 'Liliana', 0, 'supervisor', 'habilitado', '2025-09-16 09:15:29');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` smallint(3) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
