import React, { InputHTMLAttributes, ReactNode } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    icon?: ReactNode;
    rightIcon?: ReactNode;
}

const Input: React.FC<InputProps> = ({
    label,
    error,
    icon,
    rightIcon,
    className = '',
    ...props
}) => {
    return (
        <div className="w-full mb-4">
            {label && (
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    {label}
                </label>
            )}
            <div className="relative">
                {icon && (
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                        {icon}
                    </div>
                )}
                <input
                    className={`
                        w-full h-12 rounded-xl 
                        bg-slate-50
                        border ${error ? 'border-red-500' : 'border-slate-200'}
                        text-slate-900
                        placeholder:text-slate-400 
                        focus:outline-none focus:ring-2 focus:ring-primary/50 
                        transition-all
                        ${icon ? 'pl-11' : 'pl-4'}
                        ${rightIcon ? 'pr-11' : 'pr-4'}
                        ${className}
                    `}
                    {...props}
                />
                {rightIcon && (
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
                        {rightIcon}
                    </div>
                )}
            </div>
            {error && (
                <p className="mt-1.5 text-xs text-red-500 font-medium">
                    {error}
                </p>
            )}
        </div>
    );
};

export default Input;
