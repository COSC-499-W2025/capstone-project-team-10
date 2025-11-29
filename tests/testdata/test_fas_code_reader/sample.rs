// Sample Rust file for testing library extraction
use std::collections::HashMap;
use std::io::Result;
use tokio::runtime::Runtime;
use crate::internal::module;
use self::local_function;
use super::parent_module;
use super::super::grandparent;

fn helper() {
    println!("I'm a helper");
}

struct Animal {
    name: String,
}

impl Animal {
    fn speak(&self) {
        println!("Animal sound");
    }
}

fn main() {
    for i in 1..6 {
        for j in 1..6 {
            println!("i is: {}", i);
            println!("j is: {}", j);
        }
    }
}