<?php

require_once './local/helper.php';
include '../parent/config.php';
require 'vendor/autoload.php';

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Doctrine\ORM\EntityManager;

class MyClass {
    public function test() {
        echo "Hello, PHP!";
    }

?>