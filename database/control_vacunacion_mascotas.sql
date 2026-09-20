-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 20-09-2026 a las 07:51:33
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
-- Base de datos: `control_vacunacion_mascotas`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `catalogo_producto`
--

CREATE TABLE `catalogo_producto` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo` enum('vacuna','desparasitante_interno','desparasitante_externo','desparasitante_ambos') NOT NULL,
  `intervalo_dias` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mascota`
--

CREATE TABLE `mascota` (
  `id` int(11) NOT NULL,
  `propietario_id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `especie` varchar(50) NOT NULL,
  `raza` varchar(100) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `peso` decimal(5,2) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registro_aplicacion`
--

CREATE TABLE `registro_aplicacion` (
  `id` int(11) NOT NULL,
  `mascota_id` int(11) NOT NULL,
  `catalogo_id` int(11) NOT NULL,
  `veterinario_id` int(11) NOT NULL,
  `fecha_aplicacion` date NOT NULL,
  `fecha_proxima` date DEFAULT NULL,
  `dosis` varchar(50) DEFAULT NULL,
  `observaciones` varchar(255) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(150) NOT NULL,
  `contrasena_hash` varchar(255) NOT NULL,
  `rol` enum('propietario','veterinario') NOT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `nombre`, `correo`, `contrasena_hash`, `rol`, `estado`, `fecha_registro`) VALUES
(1, 'Vale Alvarez', 'vale@test.com', '$2b$12$wy0TUlRmSh.udTh/3kSr5OFyN0wf/TnqB8iykobiIPqOtlllQRHs2', 'propietario', 'activo', '2026-09-20 04:44:11'),
(2, 'Mauro Sanchez', 'mauro@test.com', '$2b$12$WpjA6wPiJadYa.ESXpvS3OZarvCLg2ToSBGuOXPuSsURuXKvejJ/a', 'veterinario', 'activo', '2026-09-20 04:51:47');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `catalogo_producto`
--
ALTER TABLE `catalogo_producto`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `mascota`
--
ALTER TABLE `mascota`
  ADD PRIMARY KEY (`id`),
  ADD KEY `propietario_id` (`propietario_id`);

--
-- Indices de la tabla `registro_aplicacion`
--
ALTER TABLE `registro_aplicacion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `mascota_id` (`mascota_id`),
  ADD KEY `catalogo_id` (`catalogo_id`),
  ADD KEY `veterinario_id` (`veterinario_id`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `catalogo_producto`
--
ALTER TABLE `catalogo_producto`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `mascota`
--
ALTER TABLE `mascota`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `registro_aplicacion`
--
ALTER TABLE `registro_aplicacion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `mascota`
--
ALTER TABLE `mascota`
  ADD CONSTRAINT `mascota_ibfk_1` FOREIGN KEY (`propietario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `registro_aplicacion`
--
ALTER TABLE `registro_aplicacion`
  ADD CONSTRAINT `registro_aplicacion_ibfk_1` FOREIGN KEY (`mascota_id`) REFERENCES `mascota` (`id`),
  ADD CONSTRAINT `registro_aplicacion_ibfk_2` FOREIGN KEY (`catalogo_id`) REFERENCES `catalogo_producto` (`id`),
  ADD CONSTRAINT `registro_aplicacion_ibfk_3` FOREIGN KEY (`veterinario_id`) REFERENCES `usuario` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
