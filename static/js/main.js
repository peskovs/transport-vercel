document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.querySelector('.md\:hidden button');
    const mobileMenu = document.querySelector('nav.hidden.md\:flex');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            if (mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.remove('hidden');
                mobileMenu.classList.add('flex', 'flex-col', 'absolute', 'top-16', 'right-4', 'bg-blue-600', 'p-4', 'rounded', 'shadow-lg', 'z-50');
            } else {
                mobileMenu.classList.add('hidden');
                mobileMenu.classList.remove('flex', 'flex-col', 'absolute', 'top-16', 'right-4', 'bg-blue-600', 'p-4', 'rounded', 'shadow-lg', 'z-50');
            }
        });
    }
    
    // close notifications after 5 seconds
    const notifications = document.querySelectorAll('.container.mx-auto.px-4.py-4 > div');
    notifications.forEach(notification => {
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease-out';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 500);
        }, 5000);
    });
});




