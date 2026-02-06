import React, { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
    children,
    variant = 'primary',
    size = 'md',
    loading = false,
    fullWidth = false,
    className = '',
    disabled,
    ...props
}) => {
    const baseStyles = 'inline-flex items-center justify-center font-semibold transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100 rounded-xl';

    const variantStyles = {
        primary: 'bg-primary hover:bg-blue-600 text-white shadow-lg shadow-primary/30',
        secondary: 'bg-slate-200 hover:bg-slate-300 text-slate-900',
        outline: 'border border-slate-200 hover:bg-slate-50 text-slate-700',
    };

    const sizeStyles = {
        sm: 'px-3 py-1.5 text-xs',
        md: 'px-6 py-2.5 text-sm',
        lg: 'px-8 py-3 text-base',
    };

    const widthStyles = fullWidth ? 'w-full' : '';

    return (
        <button
            className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyles} ${className}`}
            disabled={loading || disabled}
            {...props}
        >
            {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
            ) : null}
            {children}
        </button>
    );
};

export default Button;
