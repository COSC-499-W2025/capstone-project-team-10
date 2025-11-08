require 'rails'
require 'activerecord'
require 'sinatra'
require_relative 'helper'
require_relative './local/config'
require '../parent/module'

class MyApp
  def initialize
    puts "Hello, Ruby!"
  end
end