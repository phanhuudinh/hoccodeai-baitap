import { useEffect, useMemo, useState } from "react";
import OpenAI from 'openai';

function isBotMessage(message){
	return message.role === "assistant";
}

const LLM_BASE_URL = "http://localhost:1234/v1";
const MODEL = "hermes-3-llama-3.1-8b";

function App(){
	const [messages, setMessages] = useState("");
	const [chatHistory, setChatHistory] = useState([]);
	const [apiKey, setApiKey] = useState("");
	const client = useMemo(() => {
		return new OpenAI({
			baseURL: LLM_BASE_URL,
			apiKey: apiKey,
			dangerouslyAllowBrowser: true
		});
	}, [apiKey]);

	useEffect(() => {
		const botMessage = {
			role: "assistant",
			content: "Hello! How are you?",
		}

		setChatHistory([...chatHistory, botMessage])
	}, [])

	const submitForm = (e) => {
		e.preventDefault()

		const userMessage = {
			role: "user",
			content: messages,
		}
		setChatHistory([...chatHistory, userMessage])
		setMessages("")
	}

	useEffect(() => {
		const fetchLLMResponse = async () => {
			if (chatHistory.length > 0 && !isBotMessage(chatHistory[chatHistory.length - 1])) {
				const stream = await client.chat.completions.create({
					model: MODEL,
					messages: chatHistory,
					stream: true
				});

				for await (const event of stream) {
					if (event.choices[0].delta.content) {
						setChatHistory((prev) => {
							let lastMessage = prev[prev.length - 1];
							const botMessage = {
								role: "assistant",
								content: event.choices[0].delta.content,
							}
							if (isBotMessage(lastMessage)) {
								botMessage.content = lastMessage.content + botMessage.content;
								return [...prev.slice(0, prev.length - 1), botMessage]
							} else {
								return [...prev, botMessage];
							}
						});
					}
				}
			}
		};

		fetchLLMResponse();
	}, [chatHistory]);
	return (
		<div className="bg-gray-100 h-screen flex flex-col">
			<div className="container mx-auto p-4 flex flex-col h-full max-w-2xl">
				<h1 className="text-2xl font-bold mb-4">ChatUI với React + OpenAI</h1>
				<div className="mb-4">
					<label className="mr-2 text-gray-700">API Key:</label>
					<input
						type="password"
						placeholder="Nhập API Key của bạn"
						className="border border-gray-300 p-2 rounded flex-grow"
						value={apiKey}
						onChange={(e) => setApiKey(e.target.value)}
					/>
				</div>
				<form className="flex" onSubmit={submitForm}>
					<input
						type="text"
						placeholder="Tin nhắn của bạn..."
						className="flex-grow p-2 rounded-l border border-gray-300"
						value={messages}
						onChange={(e) => setMessages(e.target.value)}
					/>
					<button
						type="submit"
						className="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
					>
						Gửi tin nhắn
					</button>
				</form>

				<div className="flex-grow overflow-y-auto mt-4 bg-white rounded shadow p-4">
					{chatHistory.map((chatMessage, index) => (
						<div className={"mb-2" + (!isBotMessage(chatMessage) ? " text-right" : "")} key={index}>
							<p className="text-gray-600 text-sm">{isBotMessage(chatMessage) ? "Bot" : "User"}</p>
							<p className={"bg-blue-100 p-2 rounded-lg inline-block chat-message " + (isBotMessage(chatMessage) ? "bot" : "user")}>{chatMessage.content}</p>
						</div>
					))}
				</div>
			</div>
		</div>
	);
}

export default App;