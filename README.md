# Carimbo+

Aplicação Flask para controle de ocorrências de carimbos, seguindo a referência visual enviada.

## Rodar no Replit

```bash
uv run python main.py
```

O preview usa dados locais quando `ACCESS_DB_PATH` não está definido. Para testar:

- Chapa: `123456`
- Senha: `1234`

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

O Microsoft Access/driver ODBC é suportado normalmente em Windows. O preview Linux do Replit usa o repositório local para permitir desenvolvimento da interface e do fluxo enquanto o `.accdb` não estiver disponível.