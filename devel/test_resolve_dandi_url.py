import aiohttp


url = 'https://api.dandiarchive.org/api/assets/6864d7f3-08cf-4ae9-bf47-bf29048b7f7b/download/'

# do a head request and get the redirect url

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.head(url, allow_redirects=True) as resp:
            print(resp.url)
            print(resp.status)
            print(resp.headers)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())