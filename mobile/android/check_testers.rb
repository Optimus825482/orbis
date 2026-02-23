require "google/apis/androidpublisher_v3"
require "googleauth"

s = Google::Apis::AndroidpublisherV3::AndroidPublisherService.new
s.authorization = Google::Auth::ServiceAccountCredentials.make_creds(
  json_key_io: File.open("fastlane/orbis-ffa9e-e53b55f5ade2.json"),
  scope: "https://www.googleapis.com/auth/androidpublisher"
)

package = "com.orbisastro.orbis"

# Edit oluştur
e = s.insert_edit(package)
edit_id = e.id

# Tüm track'leri kontrol et
puts "=" * 60
puts "ORBIS - Google Play Track Durumu"
puts "=" * 60

tracks = s.list_edit_tracks(package, edit_id)
tracks.tracks.each do |t|
  puts "\n--- Track: #{t.track.upcase} ---"
  if t.releases.nil? || t.releases.empty?
    puts "  Sürüm yok"
  else
    t.releases.each do |r|
      puts "  Version Codes: #{r.version_codes&.join(', ')}"
      puts "  Name: #{r.name}"
      puts "  Status: #{r.status}"
      puts "  User Fraction: #{r.user_fraction || 'Tam sunum'}"
      if r.release_notes
        r.release_notes.each do |note|
          puts "  Note (#{note.language}): #{note.text}"
        end
      end
    end
  end
end

# Testers bilgisi - alpha track
puts "\n" + "=" * 60
puts "KAPALI TEST (ALPHA) - Test Kullanıcıları"
puts "=" * 60

begin
  testers = s.list_edit_testers(package, edit_id, "alpha")
  if testers.google_groups && !testers.google_groups.empty?
    puts "Google Grupları: #{testers.google_groups.join(', ')}"
  end
  if testers.google_plusCommunities && !testers.google_plusCommunities.empty?
    puts "Google+ Toplulukları: #{testers.google_plusCommunities.join(', ')}"
  end
rescue => ex
  puts "Test kullanıcı bilgisi alınamadı: #{ex.message}"
end

s.delete_edit(package, edit_id)
puts "\nBitti."
