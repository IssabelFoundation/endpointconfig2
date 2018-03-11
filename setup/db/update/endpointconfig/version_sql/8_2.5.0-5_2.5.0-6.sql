
/* Modelos asociados a FANVIL */
INSERT INTO `model` (`id_manufacturer`, `name`, `description`, `max_accounts`, `static_ip_supported`, `dynamic_ip_supported`, `static_prov_supported`) VALUES
((SELECT `id` FROM manufacturer WHERE `name` = "Fanvil"), 'X6', 'X6', '1', '1', '1', '1');
INSERT INTO `model` (`id_manufacturer`, `name`, `description`, `max_accounts`, `static_ip_supported`, `dynamic_ip_supported`, `static_prov_supported`) VALUES
((SELECT `id` FROM manufacturer WHERE `name` = "Fanvil"), 'X4', 'X4', '1', '1', '1', '1');
INSERT INTO `model` (`id_manufacturer`, `name`, `description`, `max_accounts`, `static_ip_supported`, `dynamic_ip_supported`, `static_prov_supported`) VALUES
((SELECT `id` FROM manufacturer WHERE `name` = "Fanvil"), 'H5', 'H5', '1', '1', '1', '1');
INSERT INTO `model` (`id_manufacturer`, `name`, `description`, `max_accounts`, `static_ip_supported`, `dynamic_ip_supported`, `static_prov_supported`) VALUES
((SELECT `id` FROM manufacturer WHERE `name` = "Fanvil"), 'i20S', 'i20S', '1', '1', '1', '1');


/* Propiedades de los modelos FANVIL */
INSERT INTO `model_properties` (`id_model`, `property_key`, `property_value`) VALUES
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X6"), 'max_sip_accounts', '6'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X6"), 'max_iax2_accounts', '0'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X6"), 'http_username', 'admin'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X6"), 'http_password', 'admin');
INSERT INTO `model_properties` (`id_model`, `property_key`, `property_value`) VALUES
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X4"), 'max_sip_accounts', '4'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X4"), 'max_iax2_accounts', '0'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X4"), 'http_username', 'admin'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X4"), 'http_password', 'admin');
INSERT INTO `model_properties` (`id_model`, `property_key`, `property_value`) VALUES
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "H5"), 'max_sip_accounts', '1'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "H5"), 'max_iax2_accounts', '0'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "H5"), 'http_username', 'admin'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "H5"), 'http_password', 'admin');
INSERT INTO `model_properties` (`id_model`, `property_key`, `property_value`) VALUES
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "i20S"), 'max_sip_accounts', '1'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "i20S"), 'max_iax2_accounts', '0'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "i20S"), 'http_username', 'admin'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "i20S"), 'http_password', 'admin');
