mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
[theme]\n\
base = \"dark\"\n\
secondaryBackgroundColor = \"#111111\"\n\

" > ~/.streamlit/config.toml


