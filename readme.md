docker DB: docker-compose up
backend: python run.py
frotend: cd frontend -> npm run start

access DB: - docker exec -it stock_advisor_db bash
           - psql -U user -d stock_advisor
           - select * from prediction_summary
           - <SQL code>

- newsapi
- newscatcher

dark light done


find an easy way to show error message from backend
make input field for stock symbol always upper case

jwt auth
charts stock price
dropdown on Stock Symbol Input field (based on companies in DB)
automatic stock price update
    - extra info when day is a weekend day