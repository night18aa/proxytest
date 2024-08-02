import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading

# Função para testar um proxy
def test_proxy(proxy):
    try:
        start_time = time.time()
        response = requests.get('http://www.example.com', proxies={'http': proxy, 'https': proxy}, timeout=10)
        end_time = time.time()
        response_time = end_time - start_time
        if response.status_code == 200:
            return proxy, response_time, 'Success'
        else:
            return proxy, response_time, 'Failed'
    except Exception as e:
        return proxy, None, f'Error: {str(e)}'

# Função para testar todos os proxies
def test_proxies(proxies, result_text):
    working_proxies = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                proxy, response_time, status = result
                result_text.insert(tk.END, f'Proxy {proxy} is working. Response time: {response_time:.2f} seconds.\n' if status == 'Success' else f'Proxy {proxy} failed. Status: {status}\n')
                result_text.see(tk.END)
                if status == 'Success':
                    working_proxies.append(proxy)
            except Exception as exc:
                result_text.insert(tk.END, f'Proxy {proxy} failed. Status: Error: {str(exc)}\n')
                result_text.see(tk.END)
    
    # Salvando proxies que funcionam em um arquivo
    with open('Working.txt', 'w') as file:
        for proxy in working_proxies:
            file.write(proxy + '\n')

    return working_proxies

# Função para carregar os proxies de um arquivo
def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies

# Função para iniciar o teste de proxies
def start_testing(file_path, result_text):
    proxies = load_proxies(file_path)
    result_text.delete(1.0, tk.END)
    test_proxies(proxies, result_text)
    messagebox.showinfo("Finished", "Proxy testing completed")

# Função para selecionar o arquivo e iniciar a thread de teste de proxies
def load_and_test_proxies(result_text):
    file_path = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])
    if file_path:
        threading.Thread(target=start_testing, args=(file_path, result_text)).start()

# Configuração da interface gráfica
root = tk.Tk()
root.title('Proxy Tester')
root.geometry('600x400')

frame = tk.Frame(root)
frame.pack(pady=20)

load_button = tk.Button(frame, text='Load Proxy List', command=lambda: load_and_test_proxies(result_text))
load_button.pack()

result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
result_text.pack(pady=20)

root.mainloop()
