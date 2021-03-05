
/* Modelos asociados a FANVIL */
INSERT INTO `model` (`id_manufacturer`, `name`, `description`, `max_accounts`, `static_ip_supported`, `dynamic_ip_supported`, `static_prov_supported`) VALUES
((SELECT `id` FROM manufacturer WHERE `name` = "Fanvil"), 'X1', 'X1', '2', '1', '1', '1');

/* Propiedades de los modelos FANVIL */
INSERT INTO `model_properties` (`id_model`, `property_key`, `property_value`) VALUES
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X1"), 'max_sip_accounts', '2'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X1"), 'max_iax2_accounts', '0'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X1"), 'http_username', 'admin'),
((SELECT model.id FROM manufacturer, model WHERE manufacturer.id = model.id_manufacturer AND manufacturer.name = "Fanvil" AND model.name = "X1"), 'http_password', 'admin');
