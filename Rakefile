desc "Generate all data sets"
task :data => ["data/synonyms.msgpack", "data/ngrams.msgpack"]

file "data/synonyms.msgpack" do
	mkdir_p "data"
	sh "python pycryptics/data_generators/generate_synonyms.py"
end

file "data/ngrams.msgpack" do
	sh "python pycryptics/data_generators/generate_ngrams.py"
end

file "en/__init__.py" do
	sh "git submodule update --init""
end

desc "Serve crypticweb locally"
task :serve => [:data, :compile_templates] do
	sh "python pycryptics/crypticweb/server.py"
end

task :test => [:data] do
	sh "python -m nose --nocapture pycryptics"
end

task :puz => [:data] do
	sh "python pycryptics/solve_puz.py sample_puzzles/kegler_cryptic_1.puz"
end

wordnet_path = "~/nltk_data"

task :download_corpus => [wordnet_path + "/corpora/wordnet.zip"]

file wordnet_path + "/corpora/wordnet.zip" do
	sh "python -m nltk.downloader -d " + wordnet_path + " wordnet"
end

desc "Download the NLTK wordnet corpus and the en module"
task :download => [:download_corpus, "en/__init__.py"]

desc "Generate the App Engine app"
task :app => ["app_build/data/ngrams.00.pck",
	          "app_build/data/synonyms.00.pck",
			  "app_build/en/__init__.py",
			  "app_build/nltk/__init__.py",
			  "app_build/nltk_data/corpora/wordnet.zip",
			  "app_build/web/__init__.py",
			  :compile_templates,
			  :copy_indicators,
			  :copy_python,
			  :copy_static,
			  :copy_app]

task :app_serve => [:app] do
	sh "dev_appserver.py app_build"
end

task :app_upload => [:app] do
	sh "appcfg.py update app_build"
end

file "app_build/data/ngrams.00.pck" => ["data/ngrams.00.pck"] do
	sh "mkdir -p app_build/data"
	sh "cp data/ngrams.* app_build/data/"
	sh "cp data/initial_ngrams.* app_build/data/"
end

file "app_build/data/synonyms.00.pck" => ["data/synonyms.00.pck"] do
	sh "cp data/synonyms.* app_build/data/"
end

file "app_build/en/__init__.py" => ["en/__init__.py"] do
	sh "cp -r en app_build/"
end

file "app_build/nltk/__init__.py" => ["app/nltk/__init__.py"] do
	sh "cp -r app/nltk app_build/"
end

file "app_build/web/__init__.py" do
	sh "cp -r /usr/local/lib/python2.7/site-packages/web app_build/"
end

file "app_build/nltk_data/corpora/wordnet.zip" do
	sh "mkdir -p app_build/nltk_data/corpora"
	sh "cp -r /usr/share/nltk_data/corpora/wordnet* app_build/nltk_data/corpora"
end

task :compile_templates do
	Dir.chdir "pycryptics/crypticweb"
	sh "python -m web.template --compile templates"
	Dir.chdir "../.."
end

task :copy_python do
	sh "cp -r pycryptics app_build/"
end

task :copy_static do
	sh "cp -r static app_build/"
end

task :copy_indicators do
	sh "cp -r indicators app_build/"
end

task :copy_app do
	sh "cp -r app/* app_build/"
end
