-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 17-09-2025 a las 17:45:46
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
-- Estructura de tabla para la tabla `actividades`
--

CREATE TABLE `actividades` (
  `id` int(11) NOT NULL,
  `id_usuario` smallint(3) UNSIGNED NOT NULL,
  `actividad` varchar(100) NOT NULL,
  `insumos` varchar(255) NOT NULL,
  `observaciones` text DEFAULT NULL,
  `evidencia` varchar(255) DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `actividades`
--

INSERT INTO `actividades` (`id`, `id_usuario`, `actividad`, `insumos`, `observaciones`, `evidencia`, `fecha`) VALUES
(1, 36, 'cosecha mani', 'Fertilizantes', 'asdwasdw', '44f88491da61441bb8aa99d8828ea549.jpg', '2025-09-17 15:41:07');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cultivos`
--

CREATE TABLE `cultivos` (
  `id_cultivo` smallint(3) UNSIGNED NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `id_usuario` smallint(3) UNSIGNED NOT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` varchar(20) DEFAULT 'Habilitado'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cultivos`
--

INSERT INTO `cultivos` (`id_cultivo`, `nombre`, `tipo`, `id_usuario`, `fecha_registro`, `estado`) VALUES
(6, 'Maiz', 'Siembra', 37, '2025-09-12 00:30:50', 'Habilitado'),
(7, 'Cafe', 'Cosecha', 36, '2025-09-13 02:36:24', 'Habilitado'),
(8, 'Limon', 'Cosecha', 36, '2025-09-13 02:36:32', 'Inhabilitado'),
(9, 'Mani', 'Siembra', 36, '2025-09-13 02:36:42', 'Habilitado'),
(10, 'Papa', 'Siembra', 37, '2025-09-16 03:25:34', 'Habilitado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `siembra`
--

CREATE TABLE `siembra` (
  `id_siembra` smallint(3) NOT NULL,
  `fecha_siembra` date NOT NULL,
  `detalle` text NOT NULL,
  `cod_cultivos` smallint(3) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `siembra`
--

INSERT INTO `siembra` (`id_siembra`, `fecha_siembra`, `detalle`, `cod_cultivos`) VALUES
(19, '2025-09-19', 'rthtrhytjtyj', 12);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitud_insumo`
--

CREATE TABLE `solicitud_insumo` (
  `id` int(10) UNSIGNED NOT NULL,
  `usuario_id` smallint(5) UNSIGNED NOT NULL,
  `tipo_insumo` varchar(50) NOT NULL,
  `cantidad` varchar(100) NOT NULL,
  `observaciones` text NOT NULL,
  `fecha_solicitud` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `solicitud_insumo`
--

INSERT INTO `solicitud_insumo` (`id`, `usuario_id`, `tipo_insumo`, `cantidad`, `observaciones`, `fecha_solicitud`) VALUES
(1, 37, 'Insecticidas', '123', 'sADASD', '2025-09-16 16:32:27'),
(2, 37, 'Insecticidas', '1234', 'Holaqhace', '2025-09-16 16:36:34'),
(3, 37, 'Insecticidas', '123', 'asdasd', '2025-09-16 16:38:31'),
(4, 36, 'Fertilizantes', '12', 'Necesito eso', '2025-09-17 02:27:46');

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

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id_venta` int(11) NOT NULL,
  `cod_cultivo` smallint(3) UNSIGNED NOT NULL,
  `fecha_venta` date NOT NULL,
  `cantidad_bultos` int(11) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`id_venta`, `cod_cultivo`, `fecha_venta`, `cantidad_bultos`, `precio`, `descripcion`) VALUES
(2, 8, '2025-09-15', 6, 290000.00, 'cliente carlos pipo'),
(3, 8, '2025-09-10', 13, 1000000.00, 'Fruver de la 80 exportacion tatatat'),
(5, 6, '2025-09-05', 12, 99999999.99, 'sdsfvsdvsdvsdvsdvsdvsdv');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `actividades`
--
ALTER TABLE `actividades`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `cultivos`
--
ALTER TABLE `cultivos`
  ADD PRIMARY KEY (`id_cultivo`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `siembra`
--
ALTER TABLE `siembra`
  ADD PRIMARY KEY (`id_siembra`),
  ADD KEY `cod_cultivos` (`cod_cultivos`);

--
-- Indices de la tabla `solicitud_insumo`
--
ALTER TABLE `solicitud_insumo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_usuario` (`usuario_id`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id_venta`),
  ADD KEY `fk_ventas_cultivos` (`cod_cultivo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `actividades`
--
ALTER TABLE `actividades`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `cultivos`
--
ALTER TABLE `cultivos`
  MODIFY `id_cultivo` smallint(3) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `siembra`
--
ALTER TABLE `siembra`
  MODIFY `id_siembra` smallint(3) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `solicitud_insumo`
--
ALTER TABLE `solicitud_insumo`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` smallint(3) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id_venta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `actividades`
--
ALTER TABLE `actividades`
  ADD CONSTRAINT `actividades_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `cultivos`
--
ALTER TABLE `cultivos`
  ADD CONSTRAINT `cultivos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `solicitud_insumo`
--
ALTER TABLE `solicitud_insumo`
  ADD CONSTRAINT `fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `fk_ventas_cultivos` FOREIGN KEY (`cod_cultivo`) REFERENCES `cultivos` (`id_cultivo`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
