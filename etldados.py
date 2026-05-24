import os
import pandas as pd


def padronizar_planilha(caminho_arquivo_entrada, caminho_arquivo_saida):

    try:

        # 1. Carrega o arquivo
        df = pd.read_csv(
            caminho_arquivo_entrada,
            skiprows=2,
            encoding="utf-8"
        )

        # 2. Limpa espaços dos nomes das colunas
        df.columns = df.columns.str.strip()

        # 3. Remove linhas vazias
        df.dropna(how="all", inplace=True)

        # 4. Padroniza textos
        for coluna in df.columns:

            if df[coluna].dtype == "object":

                df[coluna] = (
                    df[coluna]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

        # 5. Tratamento da coluna CIDADE
        if "CIDADE" in df.columns:

            # Cria coluna ESTADO
            df["ESTADO"] = ""

            # Percorre linha por linha
            for i in df.index:

                valor = str(df.at[i, "CIDADE"])

                # Verifica se possui "-"
                if "-" in valor:

                    cidade, estado = valor.split("-", 1)

                    # Atualiza cidade
                    df.at[i, "CIDADE"] = cidade.strip()

                    # Atualiza estado
                    df.at[i, "ESTADO"] = estado.strip()

                else:

                    # Caso não tenha estado
                    df.at[i, "CIDADE"] = valor.strip()

                    df.at[i, "ESTADO"] = ""

        # 6. Remove colunas Unnamed
        df = df.loc[
            :,
            ~df.columns.str.contains("^Unnamed", case=False)
        ]

        # 7. Remove duplicados
        df.drop_duplicates(inplace=True)

        # 8. Salva CSV tratado
        df.to_csv(
            caminho_arquivo_saida,
            index=False,
            encoding="utf-8-sig"
        )

        print(
            f"✓ Arquivo tratado com sucesso!\n"
            f"Arquivo salvo em: {caminho_arquivo_saida}"
        )
    # Tratamentos de erros
    except FileNotFoundError:

        print(
            f"✕ Arquivo não encontrado:\n"
            f"{caminho_arquivo_entrada}"
        )

    except pd.errors.EmptyDataError:

        print(
            "✕ O arquivo CSV está vazio."
        )

    except pd.errors.ParserError:

        print(
            "✕ Erro ao ler o CSV."
        )

    except UnicodeDecodeError:

        print(
            "✕ Erro de encoding."
        )

    except Exception as e:

        print(
            f"✕ Erro inesperado:\n{e}"
        )


arquivo_original = (
    "EMPRESAS CONVENIADAS PREX SITE (1) - Sheet1.csv"
)

arquivo_uniforme = (
    "empresas_conveniada_limpo.csv"
)

if __name__ == "__main__":

    padronizar_planilha(
        arquivo_original,
        arquivo_uniforme
    )
