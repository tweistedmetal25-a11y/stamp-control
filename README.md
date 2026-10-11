# Carimbo+

Aplicação desktop nativa Python para controle de ocorrências de carimbos,
criada com PySide6/Qt. O programa não usa Flask, servidor web, rotas ou API
HTTP e acessa Microsoft Access via ODBC quando configurado.

## Estrutura

```text
main.py                         Entrada da aplicação desktop
carimbo_control/
  desktop.py                    Janelas e fluxo da interface Qt
  config.py                     Configuração por ambiente
  repositories.py               Access e repositório de demonstração
  services.py                   Regras de autenticação e ocorrências
tests/                          Testes automatizados
```

## Rodar localmente

```bash
uv run python main.py
```

No modo de demonstração, preencha o login:

- Chapa: `123456`
- Senha: `1234`

Para executar os testes:

```bash
uv run python -m unittest discover -s tests -v
```

## Microsoft Access

Configure o caminho do arquivo `.accdb` e o nome do driver ODBC no ambiente onde o app será executado:

```bash
ACCESS_DB_PATH=/caminho/para/carimbos.accdb
ACCESS_ODBC_DRIVER="Microsoft Access Driver (*.mdb, *.accdb)"
```

O modo Access espera as tabelas abaixo:

```text
Colaboradores
  chapa       Texto
  nome        Texto
  senha       Texto
  perfil      Texto (operator, supervisor ou admin)
  setor       Texto
  ativo       Sim/Não

Ocorrencias
  protocolo   Texto
  chapa       Texto
  colaborador Texto
  tipo        Texto
  descricao   Texto longo
  prioridade  Texto
  status      Texto
  criado_em   Data/Hora
```

O driver Microsoft Access/ODBC normalmente está disponível em Windows. No
Replit/Linux, use o modo de demonstração ou configure um driver compatível.
O modo de demonstração pode ser desativado com `CARIMBO_DEMO=false`.
O workflow do Replit inicia a janela Qt em modo VNC.

## GitHub

O repositório está organizado como um projeto Python desktop. Os testes podem
ser executados diretamente com `uv run python -m unittest discover -s tests -v`.
Nenhum token ou senha é armazenado no código.