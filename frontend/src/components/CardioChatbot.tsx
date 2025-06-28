"use client"

import { useState } from "react"
import { Heart, Loader, Send, User, Bot, Activity } from "lucide-react"

const CardioChatbot = () => {
    const questions = [
        "🩺 Bonjour ! Commençons votre évaluation. Quel est votre âge ?",
        "🩺 Ressentez-vous des douleurs thoraciques ? (oui/non)",
        "🩺 Avez-vous des antécédents familiaux ? (oui/non)",
        "🩺 Votre fréquence cardiaque maximale mesurée ? (thalach)",
        "🩺 Niveau de dépression ST mesuré ? (oldpeak)",
        "🩺 Quel est votre type de thalassémie ? (1 = normal, 2 = fixe, 3 = réversible)",
    ]

    const [messages, setMessages] = useState([{ role: "bot", text: questions[0] }])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState(0)
    const [answers, setAnswers] = useState({})

    const progress = ((step + 1) / questions.length) * 100

    const handleSend = async () => {
        if (!input.trim()) return

        const userMessage = { role: "user", text: input }
        const newMessages = [...messages, userMessage]
        setMessages(newMessages)
        setInput("")

        const currentKey = ["age", "cp", "ca", "thalach", "oldpeak", "thal"][step]
        const cast = [
            (x) => Number.parseInt(x),
            (x) => (x.toLowerCase() === "oui" ? 1 : 0),
            (x) => (x.toLowerCase() === "oui" ? 1 : 0),
            (x) => Number.parseInt(x),
            (x) => Number.parseFloat(x),
            (x) => Number.parseInt(x),
        ]

        try {
            const value = cast[step](input.trim())
            const updatedAnswers = { ...answers, [currentKey]: value }
            setAnswers(updatedAnswers)

            if (step + 1 < questions.length) {
                setMessages([...newMessages, { role: "bot", text: questions[step + 1] }])
                setStep(step + 1)
            } else {
                setLoading(true)

                const formattedHistory = [
                    "Quel est votre âge ?", String(updatedAnswers.age),
                    "Ressentez-vous des douleurs thoraciques ? (oui/non)", updatedAnswers.cp === 1 ? "oui" : "non",
                    "Avez-vous des antécédents familiaux ? (oui/non)", updatedAnswers.ca === 1 ? "oui" : "non",
                    "Votre fréquence cardiaque maximale mesurée ? (thalach)", String(updatedAnswers.thalach),
                    "Niveau de dépression ST mesuré ? (oldpeak)", String(updatedAnswers.oldpeak),
                    "Quel est votre type de thalassémie ? (1 = normal, 2 = fixe, 3 = réversible)", String(updatedAnswers.thal),
                ]

                try {
                    const response = await fetch("http://localhost:5050/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ history: formattedHistory }),
                    })
                    const data = await response.json()
                    setMessages([...newMessages, { role: "bot", text: data.reply }])
                } catch (error) {
                    setMessages([...newMessages, { role: "bot", text: "❌ Une erreur s'est produite." }])
                }

                setLoading(false)
            }
        } catch {
            setMessages([...newMessages, { role: "bot", text: "❌ Entrée invalide. Veuillez réessayer." }])
        }
    }


    return (
        <div className="chatbot-container">
            <div className="chatbot-wrapper">
                {/* Header */}
                <div className="header">
                    <div className="header-content">
                        <div className="icon-wrapper">
                            <Heart className="heart-icon" />
                        </div>
                        <h1 className="title">Assistant Cardiologique IA</h1>
                    </div>
                    <p className="subtitle">
                        Évaluation personnalisée de votre santé cardiovasculaire grâce à l'intelligence artificielle
                    </p>
                </div>

                {/* Progress */}
                <div className="progress-card">
                    <div className="progress-header">
                        <div className="progress-label">
                            <Activity className="activity-icon" />
                            <span>Progression de l'évaluation</span>
                        </div>
                        <span className="progress-badge">
                            {step + 1} / {questions.length}
                        </span>
                    </div>
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }} />
                    </div>
                    <p className="progress-text">
                        {step < questions.length - 1 ? "Répondez aux questions pour continuer" : "Analyse en cours..."}
                    </p>
                </div>

                {/* Chat */}
                <div className="chat-card">
                    <div className="chat-header">
                        <h2 className="chat-title">
                            <Bot className="bot-icon" />
                            Consultation Virtuelle
                        </h2>
                    </div>

                    <div className="messages-container">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`message ${msg.role}`}>
                                {msg.role === "bot" && (
                                    <div className="avatar bot-avatar">
                                        <Bot className="avatar-icon" />
                                    </div>
                                )}

                                <div className={`bubble ${msg.role}-bubble`}>
                                    <p
                                        className="message-text"
                                        dangerouslySetInnerHTML={{ __html: msg.text.replace(/\n/g, "<br />") }}
                                    />
                                </div>

                                {msg.role === "user" && (
                                    <div className="avatar user-avatar">
                                        <User className="avatar-icon" />
                                    </div>
                                )}
                            </div>
                        ))}

                        {loading && (
                            <div className="message bot">
                                <div className="avatar bot-avatar">
                                    <Bot className="avatar-icon" />
                                </div>
                                <div className="bubble bot-bubble">
                                    <div className="loading-content">
                                        <Loader className="loading-spinner" />
                                        <span className="loading-text">Analyse en cours...</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="input-section">
                        <div className="input-container">
                            <input
                                type="text"
                                placeholder="Tapez votre réponse ici..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
                                disabled={loading}
                                className="input-field"
                            />
                            <button onClick={handleSend} disabled={loading || !input.trim()} className="send-button">
                                {loading ? <Loader className="button-icon spin" /> : <Send className="button-icon" />}
                            </button>
                        </div>

                        {step < questions.length && (
                            <p className="input-hint">
                                <Heart className="hint-icon" />
                                Appuyez sur Entrée pour envoyer votre réponse
                            </p>
                        )}
                    </div>
                </div>

                <div className="footer">
                    <p>⚠️ Cet outil est à des fins d'information uniquement et ne remplace pas un avis médical professionnel.</p>
                </div>
            </div>


        </div>
    )
}

export default CardioChatbot
