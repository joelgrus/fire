require 'open-uri'
require 'nokogiri'
require 'date'

require_relative 'incident'

def scrape_fire(dt)

  created = 0
  updated = 0

  fire_url = "http://www2.cityofseattle.net/fire/realTime911/getRecsForDatePub.asp?incDate=#{dt.month}/#{dt.day}/#{dt.year}&rad1=des";

  page = Nokogiri::HTML(open(fire_url));

  # all the data rows have ids like row_1, row_2, etc...
  rows = page.css('tr').find_all{|x| x["id"] =~ /^row_/};

  rows.each do |row|
    columns = row.css('td').map{|x| x.text}; # should have 6 elements
    if columns.length != 6
      continue;
    end

    #puts columns

    begin
      date =  Time.strptime(columns[0],'%m/%d/%Y %H:%M:%S %p');
    rescue
      date = Time.new(dt.year,dt.month,dt.day);
    end
    id = columns[1];
    level = columns[2].to_i;
    units = columns[3].split;
    location = columns[4];
    type = columns[5];

    incident = Incident.first(:incident_id => id);

    if incident
      #puts "updating incident #{id}";
      updated += 1
      incident.units = (incident.units + units).uniq;
      incident.first_date = [incident.first_date,date].min;
      incident.last_date = [incident.last_date,date].max;
    else
      #puts "creating new incident #{id}"
      created += 1
      incident = Incident.new;
      incident.incident_id = id;
      incident.first_date = date;
      incident.last_date = date;
      incident.level = level;
      incident.units = units;
      incident.location = location;
      incident.type = type;
    end

    incident.save;


  end

  puts "#{dt}\tcreated: #{created}\tupdated: #{updated}"


end

if ARGV
  dateparts = ARGV[0].split("-")
  year = dateparts[0].to_i
  month = dateparts[1].to_i
  day = dateparts[2].to_i
  fetch_date = Date.new(year,month,day);
else
  fetch_date = Date.new(2003,11,7); # first date, per the website
end

while fetch_date < Date.today
  scrape_fire(fetch_date)
  fetch_date = fetch_date.next_day
end