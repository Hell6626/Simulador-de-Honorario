# main.py
from config import create_app, init_database

# Cria a aplicação Flask
app = create_app()
print("==== URL MAP ====")
for r in sorted(app.url_map.iter_rules(), key=lambda x: str(x.rule)):
    print(r.methods, str(r))
print("==== FIM URL MAP ====")

if __name__ == "__main__":
    # Inicializa o banco de dados
    init_database(app)
    
    # Executa a aplicação
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
