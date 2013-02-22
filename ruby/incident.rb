# the class that represents story objects in the database

require 'mongo_mapper'

MongoMapper.database = 'fire'

class Incident
  include MongoMapper::Document
  
  key :incident_id, String
  key :first_date, Time
  key :last_date, Time

  key :level, Integer
  key :units, Array
  key :location, String
  key :type, String

  def inspect
    "id: #{self.id}\n#{incident_id}\n#{first_date}\n#{units}\n#{location}\n#{type}"
  end
end

Incident.ensure_index [[:first_date,1]]
Incident.ensure_index [[:type,1]]
Incident.ensure_index [[:incident_id,1]], :unique => true


