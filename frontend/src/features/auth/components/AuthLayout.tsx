import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChartLine, faArrowTrendUp } from '@fortawesome/free-solid-svg-icons';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthLayout: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');

    return (
        <div className="flex flex-1 min-h-screen">
            {/* Left Side: Branding / Marketing (Desktop Only) */}
            <div className="hidden lg:flex w-1/2 relative bg-slate-900 flex-col justify-between p-12 overflow-hidden">
                {/* Background Image with Overlay */}
                <div className="absolute inset-0 z-0">
                    <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"></div>
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/80 to-transparent"></div>
                </div>

                {/* Header Content */}
                <div className="relative z-10">
                    <div className="flex items-center gap-3 text-white mb-8">
                        <div className="size-8 rounded-lg bg-primary flex items-center justify-center text-white">
                            <FontAwesomeIcon icon={faChartLine} className="text-xl" />
                        </div>
                        <h2 className="text-2xl font-bold tracking-tight">WiseLab</h2>
                    </div>
                </div>

                {/* Main Marketing Content */}
                <div className="relative z-10 max-w-lg">
                    <h1 className="text-4xl xl:text-5xl font-bold leading-tight mb-6 text-white">
                        Domina tu futuro financiero con precisión.
                    </h1>
                    <p className="text-lg text-slate-400 mb-8 leading-relaxed">
                        Únete a más de 50,000 usuarios que planifican, rastrean y hacen crecer su riqueza de manera inteligente con nuestras herramientas de presupuesto basadas en espacios de trabajo.
                    </p>
                    <div className="flex gap-4 items-center">
                        <div className="flex -space-x-4 rtl:space-x-reverse">
                            <div className="w-10 h-10 border-2 border-slate-900 rounded-full bg-gradient-to-br from-blue-400 to-blue-600"></div>
                            <div className="w-10 h-10 border-2 border-slate-900 rounded-full bg-gradient-to-br from-purple-400 to-purple-600"></div>
                            <div className="w-10 h-10 border-2 border-slate-900 rounded-full bg-gradient-to-br from-pink-400 to-pink-600"></div>
                            <div className="flex items-center justify-center w-10 h-10 text-xs font-medium text-white bg-slate-700 border-2 border-slate-900 rounded-full hover:bg-slate-600">
                                +2k
                            </div>
                        </div>
                        <span className="text-sm font-medium text-slate-400">
                            Confiado por profesionales financieros
                        </span>
                    </div>
                </div>

                {/* Footer Copyright */}
                <div className="relative z-10 text-sm text-slate-500">
                    © 2026 WiseLab Inc. Todos los derechos reservados.
                </div>
            </div>

            {/* Right Side: Auth Forms */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-6 bg-background-light relative overflow-hidden">
                {/* Background Decorative Icons */}
                <div className="absolute -right-20 -bottom-20 text-[#135bec]/[0.05] pointer-events-none transform -rotate-12 select-none">
                    <FontAwesomeIcon icon={faChartLine} className="text-[400px]" />
                </div>
                <div className="absolute -left-10 -top-10 text-[#135bec]/[0.04] pointer-events-none transform rotate-12 select-none">
                    <FontAwesomeIcon icon={faArrowTrendUp} className="text-[200px]" />
                </div>

                <div className="w-full max-w-[480px] relative z-10">
                    {/* Mobile Logo (visible only on small screens) */}
                    <div className="lg:hidden flex justify-center mb-8">
                        <div className="flex items-center gap-2 text-slate-900">
                            <div className="size-8 rounded-lg bg-primary flex items-center justify-center text-white">
                                <FontAwesomeIcon icon={faChartLine} className="text-xl" />
                            </div>
                            <h2 className="text-xl font-bold">WiseLab</h2>
                        </div>
                    </div>

                    {/* Form Container */}
                    <div className="bg-white rounded-2xl shadow-2xl shadow-slate-200/50 border border-slate-200/60 p-6 sm:p-8 backdrop-blur-sm bg-white/95">
                        {/* Toggle Navigation */}
                        <div className="flex p-1 bg-slate-100 rounded-xl mb-8 relative">
                            <button
                                onClick={() => setActiveTab('login')}
                                className={`
                  flex-1 text-center py-2.5 text-sm font-semibold rounded-lg cursor-pointer transition-all duration-200
                  ${activeTab === 'login'
                                        ? 'bg-white text-primary shadow-sm'
                                        : 'text-slate-500 hover:text-slate-700'
                                    }
                `}
                            >
                                Iniciar Sesión
                            </button>
                            <button
                                onClick={() => setActiveTab('register')}
                                className={`
                  flex-1 text-center py-2.5 text-sm font-semibold rounded-lg cursor-pointer transition-all duration-200
                  ${activeTab === 'register'
                                        ? 'bg-white text-primary shadow-sm'
                                        : 'text-slate-500 hover:text-slate-700'
                                    }
                `}
                            >
                                Crear Cuenta
                            </button>
                        </div>

                        {/* Forms */}
                        {activeTab === 'login' ? <LoginForm /> : <RegisterForm />}
                    </div>

                    {/* Helper text for form switching */}
                    <div className="mt-6 text-center text-sm text-slate-500">
                        {activeTab === 'login' ? (
                            <>
                                ¿No tienes una cuenta?{' '}
                                <button
                                    onClick={() => setActiveTab('register')}
                                    className="text-primary font-bold hover:underline cursor-pointer"
                                >
                                    Regístrate ahora
                                </button>
                            </>
                        ) : (
                            <>
                                ¿Ya tienes una cuenta?{' '}
                                <button
                                    onClick={() => setActiveTab('login')}
                                    className="text-primary font-bold hover:underline cursor-pointer"
                                >
                                    Inicia sesión
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;
