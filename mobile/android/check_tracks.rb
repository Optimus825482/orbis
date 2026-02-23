require "google/apis/androidpublisher_v3"
require "googleauth"

s = Google::Apis::AndroidpublisherV3::AndroidPublisherService.new
s.authorization = Google::Auth::ServiceAccountCredentials.make_creds(
  json_key_io: File.open("fastlane/orbis-ffa9e-e53b55f5ade2.json"),
  scope: "https://www.googleapis.com/auth/androidpublisher"
)

e = s.insert_edit("com.orbisastro.orbis")
tracks = s.list_edit_tracks("com.orbisastro.orbis", e.id)

tracks.tracks.each do |t|
  puts "=== Track: #{t.track} ==="
  t.releases&.each do |r|
    puts "  Version Codes: #{r.version_codes&.join(', ')}"
    puts "  Name: #{r.name}"
    puts "  Status: #{r.status}"
    puts "  ---"
  end
end

s.delete_edit("com.orbisastro.orbis", e.id)
puts "\nDone."
