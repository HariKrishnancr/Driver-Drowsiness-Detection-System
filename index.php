<?php
/**
 * WAMP Server Entry Point for Drowsiness Detection
 * This file routes all requests through the Flask application
 */

// Set error reporting (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Get the request URI
$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Remove the base directory from the path
$base_dir = str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME']));
$path = str_replace($base_dir, '', $request_uri);

// Remove leading slash
$path = trim($path, '/');

// Handle static files (CSS, JS, images) - serve directly if they exist
if (empty($path)) {
    $path = 'index.php';
}

// Include the main application
require_once 'index.php';
