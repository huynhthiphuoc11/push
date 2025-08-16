import React from 'react';



export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {

  variant?: 'default' | 'secondary' | 'outline';

  className?: string;

}



export const Badge: React.FC<BadgeProps> = ({ variant = 'default', className = '', ...props }) => {

  const base = 'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium';

  const variants = {

    default: 'bg-gray-200 text-gray-800',

    secondary: 'bg-cyan-100 text-cyan-800',

    outline: 'border border-gray-300 text-gray-700 bg-white',

  };

  return (

    <span className={`${base} ${variants[variant]} ${className}`} {...props} />

  );

};


