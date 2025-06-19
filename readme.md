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

-> handle entering symbol which doesnt relate to any stock ('ff')

jwt auth
charts stock

     hosting on render